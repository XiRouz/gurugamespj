//////////// P O P - U P S //////////////

$('#delete-user-modal').on('show.bs.modal', function (event) {
  let url = event.relatedTarget.dataset.url;
  let form = this.querySelector('form');
  form.action = url;
  let userName = event.relatedTarget.closest('tr').querySelector('.user-name').textContent;
  this.querySelector('#user-name').textContent = userName;
})

$('#delete-game-modal').on('show.bs.modal', function (event) {
  let url = event.relatedTarget.dataset.url;
  let form = this.querySelector('form');
  form.action = url;
  let gameName = event.relatedTarget.closest('tr').querySelector('.game-name').textContent;
  this.querySelector('#game-name').textContent = gameName;
})

$('#delete-slider-modal').on('show.bs.modal', function (event) {
  let url = event.relatedTarget.dataset.url;
  let form = this.querySelector('form');
  form.action = url;
  let sliderName = event.relatedTarget.closest('tr').querySelector('.slider-name').textContent;
  this.querySelector('#slider-name').textContent = sliderName;
})

//////////// C A R O U S E L //////////////

$('#carouselExampleControls').carousel({
  interval: 5000
})

$('#carouselExampleControls').on('slide.bs.carousel', function (e) {
  if (e.direction == "left")
  {
    if (curSlider < sliderLength-1){
      curSlider++;
    }
    else{
      curSlider=0;
    }
    document.getElementById("carousel-heading").innerHTML = sl[curSlider][1];
    document.getElementById("carousel-discount").innerHTML = '-' + sl[curSlider][4] + '%';
    document.getElementById("carousel-price").innerHTML = sl[curSlider][5] + '₽';
    document.getElementById("carousel-description").innerHTML = sl[curSlider][6];
    document.getElementById("carousel-genres").innerHTML = 'Жанры: '+ sl[curSlider][8];
    carouselDiv = document.querySelector('#carouselExampleControls');
    carouselDiv.setAttribute("style", "pointer-events: none;");
    setTimeout(function(){
      carouselDiv.removeAttribute("style");
    },600);
  }
  else if (e.direction == "right")
  {
    if (curSlider > 0){
      curSlider--;
    }
    else{
      curSlider=sliderLength-1;
    }
    document.getElementById("carousel-heading").innerHTML = sl[curSlider][1];
    document.getElementById("carousel-discount").innerHTML = '-' + sl[curSlider][4] + '%';
    document.getElementById("carousel-price").innerHTML = sl[curSlider][5] + '₽';
    document.getElementById("carousel-description").innerHTML = sl[curSlider][6];
    document.getElementById("carousel-genres").innerHTML = 'Жанры: '+ sl[curSlider][8];
    carouselDiv = document.querySelector('#carouselExampleControls');
    carouselDiv.setAttribute("style", "pointer-events: none;");
    setTimeout(function(){
      carouselDiv.removeAttribute("style");
    },600);
  }
})