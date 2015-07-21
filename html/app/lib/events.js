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
    Events.timeline_events_all_cache = undefined;
    var data_callbacks = [];

    Events.set_events = function(events) {
        Events.scout = events;
        Events.timeline_events_all_cache = undefined;  // clean events caches
    };

    Events.data_ready = function(callback) {
        data_callbacks.push(callback);
    };

    Events.loadScoutEventsData = function(cb) {
        var json_file = "data/json/scout.json";
        // The JSON file could be passed as param
        if (document.URL.split('?').length > 1) {
            param = document.URL.split('?')[1].split("&")[0].split("=");
            if (param[0] === "events_file") {
                json_file = "data/json/"+param[1];
            }
        }

        if (Events.scout !== undefined) {
            cb();
        }
        else {
            $.when($.getJSON(json_file)
                    ).done(function(json_data) {
                    Events.scout = json_data.events;
                    Events.keyword = json_data.keyword;
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
    };

    function get_event_author(author, data_source, url) {
        // Convert author to common format and mangle emails
        if (data_source === "github" || data_source === "reddit" ||
            data_source === "stackoverflow" || data_source == "meetup") {
            author = "<a href='"+url+"'>"+author+"</a>";
        } else if (data_source === "mail" || data_source === "gmane") {
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
        else if (data_source === "mail" || data_source === "gmane") {
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
        if (data_source === "mail" || data_source === "gmane") {
            // mail and gmane events does not include type
            event.type = "email sent";
        }
        if (data_source === "reddit") {
            // reddit events does not include yet type
            event.type = "link";
        }
        event.isCollapsed = true; // Collapse complete body contents
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

    filterBySubject = function(event, filter_text) {
        if (filter_text === undefined) {
            return true;
        }
        var summary = event.summary.toLowerCase();
        if (event.body === null) {
            event.body = '';
        }
        var body = event.body.toLowerCase();
        var author = event.author.toLowerCase();
        var search = filter_text.toLowerCase();
        var found = (summary.indexOf(search) !== -1) ||
                    (author.indexOf(search) !== -1) ||
                    (body.indexOf(search) !== -1);
        return found;
    };


    Events.get_timeline_events = function(dss, limit, search) {
        var events_ds = Events.scout;
        var timeline_events = []; // All events to be shown in the timeline

        if (dss !== undefined && dss.length > 0) {
            events_ds = {};
            // Just include the events from dss array data sources
            $.each(Events.scout, function(data_source, events){
                if (dss.indexOf(data_source, dss) !== -1) {
                    events_ds[data_source] = Events.scout[data_source];
                }
            });
        } else {
            // Cache data in the default case (no filters)
            if (Events.timeline_events_all_cache !== undefined) {
                timeline_events = Events.timeline_events_all_cache;
            }
        }

         if (timeline_events.length === 0) {
            // First, create the common time series format:
            // [date:[d1,d2, ...], event:[e1,e2, ...]]
            $.each(events_ds, function(data_source, events){
                fields = Object.keys(events);
                $.each(events.date, function(i){
                    event = get_event(events, i, fields,data_source);
                    event[data_source] = 1;
                    event.timestamp = moment(event.date, "YYYY-MM-DD hh:mm:ss").fromNow();
                    timeline_events.push(event);
                });
            });
            // Order events in time to build a common time line
            // with the events from all data sources
            timeline_events = events_sort(timeline_events);
            if (dss === undefined || dss.length === 0) {
                Events.timeline_events_all_cache = timeline_events;
            }
         }

         if (search) {
             var timeline_events_search = [];

             // Keyword for filtering events
             $.each(timeline_events, function(index, event){
                 if (filterBySubject(event, search)) {
                     timeline_events_search.push(event);
                 }
             });
             timeline_events = timeline_events_search;
         }

        if (limit && limit <= timeline_events.length) {
            timeline_events = timeline_events.slice(0, limit);
        }

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
