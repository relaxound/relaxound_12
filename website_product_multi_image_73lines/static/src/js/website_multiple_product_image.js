$(document).ready(function ()
		{
	$(".product_multi_img").click(function ()
			{
		$('.link_detail').attr('href',this.src);
		$('.product_detail_img').attr('src',this.src);
		$('.featuredimagezoomerhidden div img').attr('src',this.src);
			});
	$(".product_main_multi_img").click(function ()
			{
		$('.link_detail').attr('href',this.src);
		$('.product_detail_img').attr('src',this.src);
		$('.featuredimagezoomerhidden div img').attr("src",this.src);
			});
	
	$(".product-zoom-image").hover(function ()
			{
		$('.zoom-innner').attr('src',this.src);	
			});

	$('#thumb-slider').owlCarousel({
		loop:false,
		margin:10,
		responsiveClass:true,
		items:4
	});  
	if ($(window).width() >= 600){
		$(".product_detail_img").hover(function() {
			$('.product_detail_img').addimagezoom({
				zoomrange : [ 3, 10 ],
				speed: 1500,
				magnifiersize : [ 300, 300 ],
				cursorshadecolor: '#fdffd5',
				magnifierpos : 'right',
				cursorshade : true,
			});
		});
	}
		});