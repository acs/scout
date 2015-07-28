// spec.js
describe('Scout timeline app', function() {

    var numCategories = 2;

    beforeEach(function() {
        browser.get('http://compose_scout_1');
        // browser.get('http://sega.bitergia.net:9090');
    });

    it('should have a title', function() {
        expect(browser.getTitle()).toEqual('Scout timeline');
    });

    it('Categories loaded', function() {
        // browser.pause();
        element(by.model('category')).evaluate('categories.length').then(
                function(count) {
                    expect(count).toEqual(numCategories);
                });
    });
});
