var TodoTxtApp = new Backbone.Marionette.Application();

TodoTxtApp.addRegions({
    contentRegion: '#content',
    editRegion: '#edit'
});


TodoTxtApp.addInitializer(function() {
    var self = this;
    var todo_collection = new TodoCollection();
    todo_collection.fetch();
    var todo_view = new TodoCompositeView({collection: todo_collection});
    this.contentRegion.show(todo_view);
    $('body').on('click', '.js-add-button', function(e) {
        self.vent.trigger('todo:add', e);
    });
    $('body').on('click', '.js-save-button', function(e) {
        self.vent.trigger('todo:save', e);
    });
});

$(function() {
    TodoTxtApp.start();
});
