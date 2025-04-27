function updateQuantity(change, itemId) {
  const input = document.getElementById(`quantity-${itemId}`);
  let value = parseInt(input.value) + change;
  if (value < 1) value = 1;
  input.value = value;
}

document.addEventListener('DOMContentLoaded', function () {
  const deleteForms = document.querySelectorAll('.delete-form');
  const clearCartForm = document.querySelector('form button[name="clear_cart"]')?.closest('form');

  deleteForms.forEach(form => {
      form.addEventListener('submit', function (e) {
          const confirmDelete = confirm('Are you sure you want to remove this product from your cart?');
          if (!confirmDelete) {
              e.preventDefault();
          }
      });
  });

  if (clearCartForm) {
      clearCartForm.addEventListener('submit', function (e) {
          const confirmClear = confirm('Are you sure you want to empty your cart? This action cannot be undone.');
          if (!confirmClear) {
              e.preventDefault();
          }
      });
  }
});
