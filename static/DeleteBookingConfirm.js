var a = document.getElementById('booking-form');
var b = document.getElementById('confirm');
var c = document.getElementById('overlay');
a.addEventListener('click', function() {
b.style.top = '300px';
b.style.opacity= '1';
b.style.display = 'block';
c.style.display = 'block';
console.log('clicked');
});