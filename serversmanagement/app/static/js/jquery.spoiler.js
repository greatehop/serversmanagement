$(document).ready(function(){
    $('.spoiler_title').click(function(){
        var show = $(this).attr('show');
        if(show == 1){
            $(this).attr('show', 0);
            $('.spoiler_block').slideUp(300);
        }else{
            $(this).attr('show', 1);
            $('.spoiler_block').slideDown(300);
        }
    });
});