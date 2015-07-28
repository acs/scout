// spec.js
describe('Scout timeline app', function() {

    var numCategories = 2;
    var events_limit = 10;
    var numDataSources = 5;
    var pageSize = 30; // used in infinite scrolling
    var scope; // angular main scope


    beforeEach(function() {
        browser.get('http://compose_scout_1');
        // browser.get('http://sega.bitergia.net:9090');
        scope = element(by.model('category'));
    });

    it('should have a title', function() {
        expect(browser.getTitle()).toEqual('Scout timeline');
    });

    it('Categories loaded', function() {
        // browser.pause();
        scope.evaluate('categories.length').then(
                function(count) {
                    expect(count).toEqual(numCategories);
                });
    });

    it('Data sources loaded', function() {
        scope.evaluate('categories[0].backends.length').then(
                function(count) {
                    expect(count).toEqual(numDataSources);
                });
    });

    it('Scout event timeline built', function() {
        // browser.pause();
        scope.evaluate('scout_events.length').then(
                function(count) {
                    expect(count).toEqual(pageSize);
                });
    });


});
