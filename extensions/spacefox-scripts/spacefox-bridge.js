(function () {
  'use strict';
  const WS_URL = 'ws://127.0.0.1:8756';
  const handlers = [];
  let socket = null;

  function connect() {
    socket = new WebSocket(WS_URL);
    socket.addEventListener('message', (event) => {
      let msg;
      try {
        msg = JSON.parse(event.data);
      } catch (e) {
        return;
      }
      for (const handler of handlers) handler(msg);
    });
    socket.addEventListener('close', () => {
      setTimeout(connect, 2000);
    });
    socket.addEventListener('error', () => {
      socket.close();
    });
  }

  connect();

  window.__spacefoxSend = function (obj) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(obj));
    }
  };

  window.__spacefoxOnMessage = function (handler) {
    handlers.push(handler);
  };
})();
