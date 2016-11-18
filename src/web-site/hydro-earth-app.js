//Tasks = new Mongo.Collection("tasks");

Models = new Mongo.Collection("models");

lpad = function(s, width, char) {
    return (s.length >= width) ? s : (new Array(width).join(char) + s).slice(-width);
}

if (Meteor.isClient) {
  // TODO: this should be solved using some cloud storage (GCS Cloud Storage, S3 buckets on Amazon)
  // Quick and dirty solution to share results.
  // Serve results~ directory as discussed here: http://stackoverflow.com/questions/17740790/dynamically-insert-files-into-meteor-public-folder-without-hiding-it

/*
  __meteor_bootstrap__.app.stack.splice (0, 0, {
    route: '/.results',
    handle: function(req, res, next) {
      // Read the proper file based on req.url 
      var filePath = process.env.PWD + '/.results/' + req.url;
      console.log(filePath);
       
      // var fs = Npm.require('fs');
      
      // var data = fs.readFileSync(filePath, data);      
  
      // res.writeHead(200, {
      //  'Content-Type': 'application/octet-stream'
      //});
      //res.write();
      //res.end();
    },
  });
*/
  
  Template.body.events({
    "click .export": function (event, template) {
        var basinId = Session.get('basinId');
        var basinLevel = Session.get('basinLevel');

        var scale = Session.get('scale');

      // Insert a task into the collection
      /*
      Tasks.insert({
        basinId: basinId,
        status: 'created',
        createdAt: new Date()
      });
      */

      var completed = function(result) {
        console.log('Completed successfully ' + basinId, result);
        var taskStatus = document.getElementById("task-status-" + basinId)
        var html = '<a target="_blank" href="' + result + '"><i class="fa fa-cloud-download"></i></a> Model input for basin ' + basinId + ': <a target="_blank" href="' + result + '">DOWNLOAD</a>';
        taskStatus.innerHTML = html;
      }

      var failed = function(_err) {
        console.log('Failed ' + basinId, _err)
        var taskStatus = document.getElementById("task-status-" + basinId)
        var html = 'Model input for basin ' + basinId + ': FAILED';
        taskStatus.innerHTML = html;
      }

      var now = new Date()
      var name = 'wflow-' + basinId + '-' + now.getFullYear() 
        + '-' + lpad(now.getMonth() + 1, 2, '0') 
        + '-' + lpad(now.getDay(), 2, '0') 
        + '_' + lpad(now.getHours(), 2, '0') 
        + '-' + lpad(now.getMinutes(), 2, '0')
        + '-' + lpad(now.getSeconds(), 2, '0');

      // Start Celery task
      var task = new CeleryTask('tasks.exportModel');
      task.call(scale, basinLevel, basinId, name).then(completed, failed); 
    }
  });

/*
  // This code only runs on the client
  Template.body.helpers({
    tasks: function () {
      if (Session.get("hideCompleted")) {
        // If hide completed is checked, filter tasks
        return Tasks.find({checked: {$ne: true}}, {sort: {createdAt: -1}});
      } else {
        // Otherwise, return all of the tasks
        return Tasks.find({}, {sort: {createdAt: -1}});
      }
    },
    hideCompleted: function () {
      return Session.get("hideCompleted");
    },
    incompleteCount: function () {
      return Tasks.find({checked: {$ne: true}}).count();
    }
  });

  Template.body.events({
    "submit .new-task": function (event) {
      // Prevent default browser form submit
      event.preventDefault();
 
      // Get value from form element
      var text = event.target.text.value;
 
      // Insert a task into the collection
      Tasks.insert({
        text: text,
        createdAt: new Date() // current time
      });
 
      // Clear form
      event.target.text.value = "";
    },
    "change .hide-completed input": function (event) {
      Session.set("hideCompleted", event.target.checked);
    }
  });
 
  Template.task.events({
    "click .toggle-checked": function () {
      // Set the checked property to the opposite of its current value
      Tasks.update(this._id, {
        $set: {checked: ! this.checked}
      });
    },
    "click .delete": function () {
      Tasks.remove(this._id);
    }
  });
*/
}

 