// JavaScript Document

	$(function(){
			//滚动显示效果
			$(window).scroll(function() {
			var scrollY = $(document).scrollTop();
			//alert($('.block1').offset().top);	
			if (scrollY >=$('.block1').offset().top){
				$('.block1 .introtit').addClass('pjump');
			}	
			if (scrollY >=$('.block2').offset().top){
				$(".block2 .blk2").addClass('blockTitcur');
			}
			if (scrollY >=$('.block3').offset().top){
				$(".block3 .blk3").addClass('blockTitcur');
			}
			if (scrollY >=$('.block4').offset().top){
				$(".block4 .blk4").addClass('blockTitcur');
			}	
			if (scrollY >=$('.block4').offset().top+450){
				//alert(1);
				$(".quickly .interFace").addClass('danru');
				$(".quickly p").addClass('xianshi');
			}	 
			})

			$(".mainSq").css("height",$(window).height()-154);
			
		})
