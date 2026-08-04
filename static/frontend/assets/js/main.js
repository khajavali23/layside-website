/* ===================================================================
    
    Author          : Valid Theme
    Template Name   :NRI- Medical & Health Template
    Version         : 1.1
    
* ================================================================= */

(function($) {
    "use strict";

    $(document).ready(function() {


        /* ==================================================
            # Wow Init
         ===============================================*/
        var wow = new WOW({
            boxClass: 'wow', // animated element css class (default is wow)
            animateClass: 'animated', // animation css class (default is animated)
            offset: 0, // distance to the element when triggering the animation (default is 0)
            mobile: true, // trigger animations on mobile devices (default is true)
            live: true // act on asynchronously loaded content (default is true)
        });
        wow.init();

        /* ==================================================
            # imagesLoaded active
        ===============================================*/
        $('#portfolio-grid,.blog-masonry').imagesLoaded(function() {

            /* Filter menu */
            $('.mix-item-menu').on('click', 'button', function() {
                var filterValue = $(this).attr('data-filter');
                $grid.isotope({
                    filter: filterValue
                });
            });

            /* filter menu active class  */
            $('.mix-item-menu button').on('click', function(event) {
                $(this).siblings('.active').removeClass('active');
                $(this).addClass('active');
                event.preventDefault();
            });

            /* Filter active */
            var $grid = $('#portfolio-grid').isotope({
                itemSelector: '.pf-item',
                percentPosition: true,
                masonry: {
                    columnWidth: '.pf-item',
                }
            });

            /* Filter active */
            $('.blog-masonry').isotope({
                itemSelector: '.blog-item',
                percentPosition: true,
                masonry: {
                    columnWidth: '.blog-item',
                }
            });

        });


         /* ==================================================
            # Fun Factor Init
        ===============================================*/
        $('.timer').countTo();
        $('.fun-fact').appear(function() {
            $('.timer').countTo();
        }, {
            accY: -100
        });
        

        /* ==================================================
            # Youtube Video Init
         ===============================================*/
        $('.player').mb_YTPlayer();


        /* ==================================================
            # Magnific popup init
         ===============================================*/
        $(".popup-link").magnificPopup({
            type: 'image',
            // other options
        });

        $(".popup-gallery").magnificPopup({
            type: 'image',
            gallery: {
                enabled: true
            },
            // other options
        });

        $(".popup-youtube, .popup-vimeo, .popup-gmaps").magnificPopup({
            type: "iframe",
            mainClass: "mfp-fade",
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false
        });

        $('.magnific-mix-gallery').each(function() {
            var $container = $(this);
            var $imageLinks = $container.find('.item');

            var items = [];
            $imageLinks.each(function() {
                var $item = $(this);
                var type = 'image';
                if ($item.hasClass('magnific-iframe')) {
                    type = 'iframe';
                }
                var magItem = {
                    src: $item.attr('href'),
                    type: type
                };
                magItem.title = $item.data('title');
                items.push(magItem);
            });

            $imageLinks.magnificPopup({
                mainClass: 'mfp-fade',
                items: items,
                gallery: {
                    enabled: true,
                    tPrev: $(this).data('prev-text'),
                    tNext: $(this).data('next-text')
                },
                type: 'image',
                callbacks: {
                    beforeOpen: function() {
                        var index = $imageLinks.index(this.st.el);
                        if (-1 !== index) {
                            this.goTo(index);
                        }
                    }
                }
            });
        });


        /* ==================================================
            # Doctor Carousel
         ===============================================*/
        $('.doctor-carousel').owlCarousel({
    loop: true,
    margin: 30,
    nav: false,
    navText: [
        "<i class='fa fa-angle-left'></i>",
        "<i class='fa fa-angle-right'></i>"
    ],
    dots: false,
    autoplay: true,

    // Timing Options
    autoplayTimeout: 3000, // Wait 3 seconds before next slide
    autoplaySpeed: 800,    // Slide animation speed
    smartSpeed: 800,  
     autoplayHoverPause: true, // Add this     // Smooth transition speed

    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1024: {
            items: 3
        }
    }
});


        /* ==================================================
            # Services Carousel
         ===============================================*/
       $('.services-carousel').owlCarousel({
    loop: true,
    margin: 30,
    nav: false,
    navText: [
        "<i class='fa fa-angle-left'></i>",
        "<i class='fa fa-angle-right'></i>"
    ],
    dots: false,

    autoplay: true,
    autoplayTimeout: 3000,     // Time before next slide (3000ms = 3 seconds)
    autoplaySpeed: 800,         // Slide animation speed (800ms)
    smartSpeed: 800, 
    autoplayHoverPause: true, // Add this           // Smooth transition speed

    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1024: {
            items: 3
        }
    }
});
        /* ==================================================
            # Testimonials Carousel
         ===============================================*/
       $('.testimonial-carousel').owlCarousel({
    loop: true,
    margin: 30,
    nav: false,
    navText: [
        "<i class='fa fa-angle-left'></i>",
        "<i class='fa fa-angle-right'></i>"
    ],
    dots: false,
    autoplay: true,

    // Timing Options
    autoplayTimeout: 3000, // Wait 3 seconds before next slide
    autoplaySpeed: 800,    // Slide animation speed
    smartSpeed: 800, 
     autoplayHoverPause: true, // Add this      // Smooth transition speed

    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1024: {
            items: 2
        }
    }
});


        /* ==================================================
            # Health Tips Carousel
         ===============================================*/
        $('.tips-carousel').owlCarousel({
            loop: true,
            nav: true,
            dots: false,
            items: 1,
            navText: [
                "<i class='fa fa-angle-left'></i>",
                "<i class='fa fa-angle-right'></i>"
            ],
        });


        /* ==================================================
            Nice Select Init
         ===============================================*/
        // $('select').niceSelect();


        /* ==================================================
            Contact Form Validations
        ================================================== */
        $('.contact-form').each(function() {
            var formInstance = $(this);
            formInstance.submit(function() {

                var action = $(this).attr('action');

                $("#message").slideUp(750, function() {
                    $('#message').hide();

                    $('#submit')
                        .after('<img src="assets/img/ajax-loader.gif" class="loader" />')
                        .attr('disabled', 'disabled');

                    $.post(action, {
                            name: $('#name').val(),
                            email: $('#email').val(),
                            phone: $('#phone').val(),
                            comments: $('#comments').val()
                        },
                        function(data) {
                            document.getElementById('message').innerHTML = data;
                            $('#message').slideDown('slow');
                            $('.contact-form img.loader').fadeOut('slow', function() {
                                $(this).remove()
                            });
                            $('#submit').removeAttr('disabled');
                        }
                    );
                });
                return false;
            });
        });

    }); // end document ready function


    /* ==================================================
        Preloader Init
    ===============================================*/
        $(window).on('load', function() {
        // Animate loader off screen
        $(".se-pre-con").fadeOut("slow");;
    });

})(jQuery); // End jQuery




setTimeout(function(){
    var el = document.querySelector(".se-pre-con");
    if (el) {
        el.style.display = "none";
    }
}, 1000);








$('.blog-carousel').owlCarousel({
    loop: true,
    margin: 30,
    nav: false,
    navText: [
        "<i class='fa fa-angle-left'></i>",
        "<i class='fa fa-angle-right'></i>"
    ],
    dots: false,
    autoplay: true,

    // Timing Options
    autoplayTimeout: 3000,
    autoplaySpeed: 800,
    smartSpeed: 800,
     autoplayHoverPause: true, // Add this

    responsive: {
        0: {
            items: 1
        },
        768: {
            items: 2
        },
        1024: {
            items: 3
        }
    }
});

function handleCarouselVisibility(selector) {
    const $carousel = $(selector);

    $(window).on('scroll', function () {
        const top = $carousel.offset().top;
        const bottom = top + $carousel.outerHeight();

        const viewportTop = $(window).scrollTop();
        const viewportBottom = viewportTop + $(window).height();

        if (viewportBottom > top && viewportTop < bottom) {
            // Carousel is visible
            $carousel.trigger('stop.owl.autoplay');
        } else {
            // Carousel is not visible
            $carousel.trigger('play.owl.autoplay', [3000]);
        }
    });
}

// Apply to all carousels
handleCarouselVisibility('.services-carousel');
handleCarouselVisibility('.doctor-carousel');
handleCarouselVisibility('.testimonial-carousel');
handleCarouselVisibility('.blog-carousel');