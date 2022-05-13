{
    console.log('The page is working')
    let slideIndex = 0;
    let a = document.getElementsByClassName('search-page-body');
    console.log(a.length);
    showSlides();

    function showSlides() {
        let i;
        let slides = document.getElementsByClassName("mySlides");
        console.log(slides.length)
        for (i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
            console.log('slide...')
        }
        slideIndex++;
        if (slideIndex > slides.length) {slideIndex = 1}
        slides[slideIndex-1].style.display = "block";
        setTimeout(showSlides, 2000); // Change image every 2 seconds
    }
}