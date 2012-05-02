var ani = {
	gross1: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	2,
		delay:	20,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	tierra1: {
		type:	'bottom',
		from:	-70,
		to:		0,
		step:	3,
		delay:	20
	},
	tierra2: {
		type:	'bottom',
		from:	-78,
		to:		0,
		step:	3,
		delay:	20
	},



	gross2: {
		type:	'bottom',
		from:	-70,
		to:		0,
		step:	5,
		delay:	20
	},
	flowers: {
		type:	'left',
		to:		0,
		step:	60,
		delay:	10
	},
	creditos: {
		type:	'top',
		to:		-4500,
		from:	300,
		step:	-1,
		delay:	20,
		onstart: function(){this.style.display = 'block'}
	},
	license: {
		type:	'top',
		to:		-18800,
		from:	0,
		step:	-1,
		delay:	20,
		onstart: function(){this.style.display = 'block'}
	},



	sun: {
		type:	'top',
		to:		0,
		from:	-147,
		step:	10,
		delay:	10,
		onstart: function(){this.style.display = 'block'}
	},
	cloud1: {
		type:	'left',
		from:	-300,
		to:		screen.availWidth,
		step:	1,
		delay:	50
	},
	cloud2: {
		type:	'left',
		from:	0,
		to:		screen.availWidth,
		step:	1,
		delay:	150,
		onstart: function(){
			this.style.display = 'block';
		}
	},
	cloud3_2: {
		type:	'left',
		from:	0,
		to:		screen.availWidth,
		step:	1,
		delay:	400,
		onstart: function(){
			this.style.display = 'block';
		}
	},
	cloud3: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	1,
		delay:	10,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	tree3_1: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	1,
		delay:	20,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	tree3_2: {
		type:	'right',
		from:	0,
		to:		7,
		step:	1,
		delay:	30,
		unit:	'%'
	},
	tree1_1: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	1,
		delay:	20,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	tree1_2: {
		type:	'right',
		from:	0,
		to:		7,
		step:	1,
		delay:	30,
		unit:	'%'
	},
	tree2_1: {
		type:	'left',
		from:	0,
		to:		-17,
		step:	1,
		delay:	10,
		unit:	'%',
		onfinish: function(){
			$fx('#tree1').fxAdd(ani.tree1_1).fxAdd(ani.tree1_2).fxRun(function(){});
		}
	},
	tree2_2: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	1,
		delay:	10,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	wrapper: {
		type:	'opacity',
		from:	100,
		to:		0,
		step:	-10,
		delay:	100,

	},
	wrapper2: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	10,
		delay:	100,

	},

	tree4_1: {
		type:	'opacity',
		from:	0,
		to:		100,
		step:	1,
		delay:	20,
		onstart: function(){this.style.display = 'block'},
		onfinish: function(){this.style.filter = ''}
	},
	tree4_2: {
		type:	'right',
		from:	0,
		to:		5,
		step:	1,
		delay:	30,
		unit:	'%'
	}



};

function startAnimation(){
	$fx('#cloud1').fxAdd(ani.cloud1).fxRun(null,-1);
	
	$fx('#tierra2').fxAdd(ani.tierra2).fxRun(function(){
		$fx('#tierra1').fxAdd(ani.tierra1).fxRun(function(){
		});
	});
	
	$fx('#tree3').fxAdd(ani.tree3_1).fxAdd(ani.tree3_2).fxHold(700).fxRun();
		$fx('#cloud2').fxAdd(ani.cloud2).fxRun(null,-1);
	$fx('#tree4').fxAdd(ani.tree4_1).fxAdd(ani.tree4_2).fxHold(1000).fxRun();
	
	$fx('#cloud3').fxAdd(ani.cloud3).fxHold(500).fxAdd(ani.cloud3_2).fxRun();
	
	$fx('#tree2').fxAdd(ani.tree2_1).fxAdd(ani.tree2_2).fxHold(1000).fxRun();
}

function displaymessage()
{
	alert("Hello World!");
}

function credits(){

	$fx('#content').fxAdd(ani.wrapper).fxRun(function(){
	$fx('#creditos').fxAdd(ani.creditos).fxRun(function(){
		$fx('#content').fxAdd(ani.wrapper2).fxRun();
	});
	});


}
function license(){

	$fx('#content').fxAdd(ani.wrapper).fxRun(function(){
	$fx('#license').fxAdd(ani.license).fxRun(function(){
		$fx('#content').fxAdd(ani.wrapper2).fxRun();
	});
	});


}


/* <![CDATA[ */
    (function() {
	            var s = document.createElement('script'), t = document.getElementsByTagName('script')[0];
		            s.type = 'text/javascript';
			            s.async = true;
				            s.src = 'http://api.flattr.com/js/0.6/load.js?mode=auto';
					            t.parentNode.insertBefore(s, t);
						        })();
/* ]]> */
