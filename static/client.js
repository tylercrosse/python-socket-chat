$(function() {
  var socket = io();

  //**** Socket Events ****//
  socket.on('connect' ,function (data) {
    console.log('connect');
  });

  socket.on('lobby message' ,function (data) {
    console.log(data.data);
  });

});
