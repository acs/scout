/*
 * Copyright (C) 2012-2015 Bitergia
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 * This file is a part of the Scout project
 *
 * Authors:
 *   Alvaro del Castillo San Felix <acs@bitergia.com>
 *
 */

var Events = {};

(function() {

    Events.scout = undefined;
    var data_callbacks = [];

    Events.data_ready = function(callback) {
        data_callbacks.push(callback);
    };

    Events.loadScoutEventsData = function(cb) {
        var json_file = "data/json/scout.json";
        if (Events.scout !== undefined) {
            cb();
        }
        else {
            $.when($.getJSON(json_file)
                    ).done(function(json_data) {
                    Events.scout = json_data;
                    if (cb) {cb();}
                    for (var j = 0; j < data_callbacks.length; j++) {
                        if (data_callbacks[j].called !== true) {
                            data_callbacks[j]();
                        }
                        data_callbacks[j].called = true;
                    }
            }).fail(function() {
                console.log("Scout widget disabled. Missing " + json_file);
            });
        }
    }

    function get_event_author(author, data_source, url) {
        // Convert author to common format abd mangle emails
        if (data_source === "github" || data_source === "reddit" ||
            data_source === "stackoverflow") {
            author = "<a href='"+url+"'>"+author+"</a>";
        } else if (data_source === "mail") {
            author = author.replace("@","_at_");
        }
        return author;
    }

    function get_event_type(type, data_source) {
        // Translate event code to human language
        var human_type = type;
        if (data_source === "github") {
            if (type == "CreateEvent") {
                human_type = "new repository";
            }
        }
        else if (data_source === "stackoverflow") {
            if (type === 1) {
                human_type = "new question";
            } else if (type == 2) {
                human_type = "new answer";
            } else if (type == 3) {
                human_type = "new comment";
            }
        }
        else if (data_source === "mail") {
            human_type = "mail sent";
        }
        return human_type;
    }

    function get_event(data, index, fields, data_source) {
        // Create a dict with event data
        event = {};
        $.each(fields, function(i) {
            var val;
            if (data[fields[i]] !== undefined) {
                val = data[fields[i]][index];
            }
            event[fields[i]] = val;
            if (fields[i] === "type") {
                event[fields[i]] = get_event_type(val, data_source);
            }
            else if (fields[i] === "author") {
                var author_url;
                if (fields.indexOf("author_url") > -1) {
                    author_url = data.author_url[index];
                } else {
                    author_url = val;
                }
                // Remove the URL from author name
                val = val.split("/").pop();
                event[fields[i]] = get_event_author(val, data_source, author_url);
            }
        });
        if (data_source === "mail") {
            // mail events does not include type
            event.type = "email sent";
        }
        if (data_source === "reddit") {
            // reddit events does not include yet type
            event.type = "link";
        }
        return event;
    }

    function events_sort(events,  field) {
        // All events include a date field
        function compare(event1, event2) {
            var res;

            date1 = Date.parse(event1.date.replace(/-/g,"/"));
            date2 = Date.parse(event2.date.replace(/-/g,"/"));

            if (date1<date2) {
                res = 1;
            }
            else if (date1>date2) {
                res = -1;
            }
            else {
                res = 0;
            }
            return res;
        }
        events.sort(compare);
        return events;
    }

    Events.get_timeline_events = function() {
        var events_ds = Events.scout;
        var timeline_events = []; // All events to be shown in the timeline

        // First, create the common time series format: [date:[d1,d2, ...], event:[e1,e2, ...]]
        $.each(events_ds, function(data_source, events){
            fields = Object.keys(events);
            $.each(events.date, function(i){
                event = get_event(events, i, fields,data_source);
                event[data_source] = 1;
                event.timestamp = moment(event.date, "YYYY-MM-DD hh:mm:ss").fromNow();
                timeline_events.push(event);
            });
        });
        // Order events in time to build a common time line with the events from all data sources
        timeline_events = events_sort(timeline_events);

        return timeline_events;
    };

    Events.highlightLimit = function (text, keyword, limit) {
        var n = text.search(new RegExp(keyword, "i"));
        var out = '';
        if (n>-1) {
            if (n-limit>0) {
                out = "..." + text.substr(n-limit,limit);
            }
            out += "<b>"+text.substr(n,keyword.length)+"</b>";
            out += text.substr(n+keyword.length,limit) +'...';
        } else {
            out = text.substr(0,80) + '...';
        }
        return out;
    };
})();

Events.loadScoutEventsData();
