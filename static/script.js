const id = localStorage.getItem('id') || cuid();
localStorage.setItem('id', id);
let input = document.getElementById('input');
let container = document.getElementById('messages');

const addMessage = (text, right) => {
  const classes = [
    'px-3', 'py-2', 'my-1', 'rounded',
    'shadow-sm', 'limited-width-sm',
    'animated', 'fadeIn', 'faster',
    (right ? 'bg-white' : 'bg-warning'),
    (right ? 'float-right' : 'float-left')
  ];
  let message = document.createElement('div');
  let clearfix = document.createElement('div');

  classes.forEach(_class => message.classList.add(_class));
  message.innerHTML = text;
  container.appendChild(message);

  clearfix.classList.add('clearfix');
  container.appendChild(clearfix);
  container.scrollTop = container.scrollHeight;
};

const sendMessage = (text, url) => {
  const options = {
    method: 'POST',
    body: JSON.stringify({id, text}),
    headers: {'Content-Type': 'application/json'}
  };
  fetch(url, options).then(response => {
    if (response.status !== 200) addMessage('...', false);
    response.json().then(data => addMessage(data.text, false));
  });
};

document.onkeydown = e => {
  input.focus();
  if (e.keyCode != 13) return;
  addMessage(input.value, true);
  sendMessage(input.value, '/chat');
  input.value = '';
};

addMessage('hey, what\'s up?', false);
