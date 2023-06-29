const modalDel = document.querySelector('.modal-del_c');
const activateDel = document.querySelector('.activate-del_c');
const cancelDel = document.querySelector('.cancel-del_c');

activateDel.addEventListener('click', function() {
  modalDel.style.display = 'block';
});

cancelDel.addEventListener('click', function() {
  modalDel.style.display = 'none';
});