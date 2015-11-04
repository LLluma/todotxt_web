var TodoTxtApp = new Backbone.Marionette.Application();

TodoTxtApp.addRegions({
    contentRegion: '#content',
    editRegion: '#edit'
});

TodoTxtApp.TodoModel = Backbone.Model.extend({
    defaults: {
        line: '',
        done: false,
        projects: [],
        contexts: []
    },
    toJSON: function() {
        var json = Backbone.Model.prototype.toJSON.apply(this, arguments);
        json.cid = this.cid;
        return json;
    }
});

TodoTxtApp.TodoCollection = Backbone.Collection.extend({
    url: '/todo/',
    model: TodoTxtApp.TodoModel
});

TodoTxtApp.TodoItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-item',
    model: TodoTxtApp.TodoModel,
    tagName: 'tr',
    className: 'todotxt__item',
    ui: {
        checkbox: '.js-checkbox'
    },
    events: {
        'change .js-checkbox': "recordTicked"
    },
    recordTicked: function(e) {
        var done = this.ui.checkbox.hasClass('is-checked');
        this.model.set('done', done);
        this.$el.toggleClass('js-done');
    },
    onRender: function() {
        componentHandler.upgradeElements(this.el);
        if (this.model.get('done')) {
            this.$el.addClass('js-done');
        }
    }
});

TodoTxtApp.TodoEditItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-edit',
    model: TodoTxtApp.TodoModel,
    className: "todotxt__edit",
    ui: {
        edit_box: '.edit_box'
    },
    events: {
        'click .js-save-item-button': "saveItem"
    },
    saveItem: function(e) {
        this.model.set('line', this.ui.edit_box.val());
        TodoTxtApp.vent.trigger('todo:new', this.model);
        this.remove();
    }
});

TodoTxtApp.TodoCompositeView = Backbone.Marionette.CompositeView.extend({
    template: '#todo-list',
    tagName: 'table',
    collection: TodoTxtApp.TodoCollection,
    childView: TodoTxtApp.TodoItemView,
    childViewContainer: 'tbody',
    className: "todotxt__list mdl-data-table mdl-js-data-table",
    initialize: function(options) {
        var self = this;
        TodoTxtApp.vent.on('todo:save', function(e) {
            self.saveTodo(e);
        });
        TodoTxtApp.vent.on('todo:add', function(e) {
            self.addTask(e);
        });
        TodoTxtApp.vent.on('todo:delete', function(e) {
            self.deleteTask(e);
        });
        TodoTxtApp.vent.on('todo:new', function(model) {
            self.collection.add(model);
            self.saveTodo();
        });
    },
    saveTodo: function(e) {
        var self = this;
        self.collection.sync('create', self.collection);
    },
    addTask: function(e, model) {
        var self = this;
        if (!model) {
            model = new TodoTxtApp.TodoModel();
        }
        var edit_view = new TodoTxtApp.TodoEditItemView({model: model});
        TodoTxtApp.editRegion.show(edit_view);
    },
    deleteTask: function(e) {
        var elem_index = e.toElement.id.slice(1) - 6;  // ids starts from id="c6" instead of id="c1"
        this.children.findByIndex(elem_index).remove();
    }
});

TodoTxtApp.addInitializer(function() {
    var self = this;
    var todo_collection = new TodoTxtApp.TodoCollection();
    todo_collection.fetch();
    var todo_view = new TodoTxtApp.TodoCompositeView({collection: todo_collection});
    this.contentRegion.show(todo_view);
    $('body').on('click', '.js-add-button', function(e) {
        self.vent.trigger('todo:add', e);
    });
    $('body').on('click', '.js-save-button', function(e) {
        self.vent.trigger('todo:save', e);
    });
    $('body').on('click', '.js-delete-item-button', function(e) {
        self.vent.trigger('todo:delete', e);
    });
});

$(function() {
    TodoTxtApp.start();
});
