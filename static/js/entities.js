TodoModel = Backbone.Model.extend({
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
    },
    serialize: function(line) {
        var result = {
            line: '',
            done: false,
            projects: [],
            contexts: []
        };
        var line_words = [];
        if (line.startsWith("x ")) {
            result.done = true;
            line = line.slice(2);
        }
        _.each(line.split(" "), function(word) {
            if (word.startsWith('+')) {
                result.projects.push(word);
            } else if (word.startsWith('@')) {
                result.contexts.push(word);
            } else {
                line_words.push(word);
            }
        });
        result.line = line_words.join(" ");
        return result;
    },
    get_unserialized: function() {
        return this.unserialize(this.model.toJSON());
    },
    unserialize: function(obj) {
        var line = [];
        if (obj.done) {
            line.push("x");
        }
        line.push(obj.line);
        line = line.concat(obj.projects);
        line = line.concat(obj.contexts);
        return line.join(" ");
    }
});

TodoCollection = Backbone.Collection.extend({
    url: '/todo/',
    model: TodoModel,
    action: function(e, action_name, opts) {
        var self = this;
        var url = self.url + action_name;
        // note that these are just $.ajax() options
        _.extend(opts, {
            url: url,
            type: 'POST'
        });
        return (this.sync || Backbone.sync).call(this, null, this, opts);
    }
});

TodoItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-item',
    model: TodoModel,
    tagName: 'tr',
    className: 'todotxt__item',
    ui: {
        checkbox: '.js-checkbox'
    },
    events: {
        'change .js-checkbox': "recordTicked",
        'click .js-delete-item-button': "deleteItem",
        'dblclick': "editItem",
        'taphold': "editItem"
    },
    recordTicked: function(e) {
        var done = this.ui.checkbox.hasClass('is-checked');
        this.model.set('done', done);
        this.$el.toggleClass('js-done');
    },
    deleteItem: function(e) {
        this.model.collection.remove(this.model);
        this.remove();
    },
    editItem: function(e) {
        TodoTxtApp.vent.trigger('todo:add', e, this.model);
    },
    onRender: function() {
        componentHandler.upgradeElements(this.el);
        if (this.model.get('done')) {
            this.$el.addClass('js-done');
        }
    }
});

TodoEditItemView = Backbone.Marionette.ItemView.extend({
    template: '#todo-edit',
    model: TodoModel,
    className: "todotxt__edit",
    ui: {
        edit_box: '.edit_box'
    },
    events: {
        'click .js-save-item-button': "saveItem"
    },
    serializeData: function() {
        var result = this.constructor.__super__.serializeData.call(this);
        result.unserialized = this.model.unserialize(result);
        console.log(result.unserialized);
        return result
    },
    saveItem: function(e) {
        this.model.set(this.model.serialize(this.ui.edit_box.val()));
        TodoTxtApp.vent.trigger('todo:new', this.model);
        this.remove();
    }
});

TodoCompositeView = Backbone.Marionette.CompositeView.extend({
    template: '#todo-list',
    tagName: 'table',
    collection: TodoCollection,
    childView: TodoItemView,
    childViewContainer: 'tbody',
    className: "todotxt__list mdl-data-table mdl-js-data-table",
    initialize: function(options) {
        var self = this;
        TodoTxtApp.vent.on('todo:save', function(e) {
            self.saveTodo(e);
        });
        TodoTxtApp.vent.on('todo:add', function(e, model) {
            self.addTask(e, model);
        });
        TodoTxtApp.vent.on('todo:archive', function(e, model) {
            self.archiveTodo(e, model);
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
    archiveTodo: function(e) {
        var self = this;
        self.collection.action(e, 'archive', {
            data: JSON.stringify(self.collection.toJSON()),
            dataType: 'json',
            success: function(result) {
                self.update_view(result);
            }
        });
    },
    update_view: function(result) {
        var self = this;
        self.collection.reset(result);
        self.render();
    },
    addTask: function(e, model) {
        var self = this;
        if (!model) {
            model = new TodoModel();
        }
        var edit_view = new TodoEditItemView({model: model});
        TodoTxtApp.editRegion.show(edit_view);
    }
});

