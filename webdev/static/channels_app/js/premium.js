const modalPre = document.querySelector('.modal-premium');
const activatePre = document.querySelector('.activate-premium');
const cancelPre = document.querySelector('.cancel-premium');

activatePre.addEventListener('click', function() {
  modalPre.style.display = 'block';
});

cancelPre.addEventListener('click', function() {
  modalPre.style.display = 'none';
});