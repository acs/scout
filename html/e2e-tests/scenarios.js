// spec.js
describe('Scout timeline app', function() {

    var numCategories = 1;
    var events_limit = 10;
    var numDataSources = 5;
    var pageSize = 30; // used in infinite scrolling
    var johnEvents = 20; // events searching for john
    var scope; // angular main scope
    var searchButton = element(by.id('search_button'));
    var searchText = element(by.model('filter_text'));
    var scope = element(by.model('category'));


    beforeEach(function() {
        browser.get('http://compose_scout_1');
        // browser.get('http://sega.bitergia.net:9090');
    });

    it('should have a title', function() {
        expect(browser.getTitle()).toEqual('Scout timeline');
    });

    it('Categories loaded', function() {
        // browser.pause();
        scope.evaluate('categories.length').then(
            function(count) {
                expect(count).toEqual(numCategories);
            }
        );
    });

    it('Data sources loaded', function() {
        scope.evaluate('categories[0].backends.length').then(
            function(count) {
                expect(count).toEqual(numDataSources);
            }
        );
    });

    it('Scout event timeline built', function() {
        // browser.pause();
        scope.evaluate('scout_events').then(
            function(events) {
                expect(events.length).toEqual(pageSize);
            }
        );
    });

    it('Data freshness', function() {
        scope.evaluate('scout_events').then(
            function(events) {
                var max_days_old = 1; // Scout daily updated
                var now = new Date();
                var day_mseconds = 60*60*24*1000;

                function isUpdated() {
                    var update = events[0].date;
                    var update_time = new Date(update);
                    var ms_old = now.getTime() - update_time.getTime();
                    var days_old = ms_old / day_mseconds;
                    days_old = parseInt(days_old, null);
                    expect(days_old).toBeLessThan(max_days_old+1,
                            "scout events is not updated.");
                }

                isUpdated();  // In the future we will do it per data source
            }
        );
        }
    );

    it('Searching for john', function() {
        searchText.sendKeys("john");
        searchButton.click();
        scope.evaluate('scout_events.length').then(
            function(john_events_found) {
                expect(john_events_found).toEqual(johnEvents);
            }
        );
    });

});
