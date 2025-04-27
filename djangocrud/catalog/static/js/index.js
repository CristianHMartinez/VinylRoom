document.addEventListener("DOMContentLoaded", function () {
    const sliderWrapper = document.querySelector(".Slider");
    const slides = document.querySelectorAll(".Slider img");
    const navLinks = document.querySelectorAll(".Slider-nav a");
    let currentIndex = 0;

    function changeSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        
        sliderWrapper.scrollTo({
            left: slides[currentIndex].offsetLeft,
            behavior: 'smooth'
        });

        navLinks.forEach((link, index) => {
            if (index === currentIndex) {
                link.style.opacity = 1;
            } else {
                link.style.opacity = 0.75;
            }
        });
    }

    setInterval(changeSlide, 5000);
});
