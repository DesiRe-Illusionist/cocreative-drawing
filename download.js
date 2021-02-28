
downloadImage = function() {
    var style_option=document.getElementById("style-select");
    var download_canvas = document.getElementById("defaultCanvas0");
    var hint=document.getElementById("hint-message");
    var image = download_canvas.toDataURL("image/jpg");

    //if style_option.selectedIndex==0:Original, do nothing
    if(style_option.selectedIndex==0)
    {
        const a = document.createElement('a');
        a.download = "co-creative-origin.png";
        a.href = image;
        document.body.appendChild(a);  
        a.click();
        a.remove();
    }

    //if style_option.selectedIndex==1:Picasso
    if(style_option.selectedIndex==1)
    {
        hint.innerHTML='Please Wait For Generating Styled Image...';
        //query for model
        const model = new rw.HostedModel({
		    url: "https://picasso-9af97d53.hosted-models.runwayml.cloud/v1/",
		    token: "O9czDzqI4Sdu1xmA5UHrCQ==",
	    });
	    const inputs = {
		    "contentImage": image
	    };
	    model.query(inputs).then(outputs => {
		    const { stylizedImage } = outputs;
            // use the outputs in your project
            hint.innerHTML='';
            const a = document.createElement('a');
            a.download = "co-creative-picasso.png";
            a.href = stylizedImage;
            document.body.appendChild(a);  
            a.click();
            a.remove();
            
	    });
        
      
    }

    
    
};