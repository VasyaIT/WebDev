const modal = document.querySelector('.modal');
const deleteBtn = document.querySelector('.delete-btn');
const cancelBtn = document.querySelector('.cancel-btn');

deleteBtn.addEventListener('click', function() {
  modal.style.display = 'block';
});

cancelBtn.addEventListener('click', function() {
  modal.style.display = 'none';
});