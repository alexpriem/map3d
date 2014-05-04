
var varsel="aant_dev";
var regioidx=1;
var date_index={};
var datesel=new Date(2013,2,1);
var chart_data=[];
var regio_ts={};
var regio_ts_min={};
var regio_ts_max={};


var controller;

var Controller =function () {

	this.x=0; -90;
	this.y=0;
	this.z=0;
};



function prep_data () {

	var records=data.length;	var row, ts,regio;
	
	prevd=0;
	start_i=0;
	dates=[];
	date_index={};
	regiocol=var_types.indexOf("regio");
	datecol=var_types.indexOf("date");
	varidx=varnames.indexOf(varsel);
	keyidx=varnames.indexOf("key");	
	datamin=data[0][varidx];
	datamax=data[0][varidx];


	ts_total=[];
	for (i=0; i<regio_keys.length;i++) {
		key=regio_keys[i];
		regio_ts[key]=[];
		regio_ts_min[key]=[];	
		regio_ts_max[key]=[];
	}
	for (i=0; i<records; i++) {
		row=data[i];
		d=row[datecol];
		regio=row[regiocol];		
		if (keyidx>=0) {					
			if (row[keyidx]!=keysel) continue;
		}

		val=row[varidx];
		if (d-prevd!=0)  {			 // stupid javascript unable to compare dates
			dates.push(d);			
			if (prevd!=0) {
				date_index[prevd]={start_row:start_i, eind_row:i-1}
				start_i=i;
				ts_total.push([prevd,total]);
			}			
			total=0;
			prevd=d;			
		}

		total+=val;
		if (val<datamin) {
			datamin=val;
		}
		if (val>datamax) {
			datamax=val;
		}		
		regio_ts[regio].push([d,val]);
		if (val<regio_ts_min[regio]) regio_ts_min[regio]=val;
		if (val>regio_ts_max[regio]) regio_ts_max[regio]=val;		
	}

	date_index[prevd]={startdatum:start_i, einddatum:i-1}
	ts_total.push([prevd,total]);

	mindate=var_min[datecol];
	maxdate=var_max[datecol];
	datesel['a']=data[0][datecol];  // init: begin met datum van eerste record.	
	datesel['b']=data[0][datecol];  // init: begin met datum van eerste record.	
	datesel['c']=data[0][datecol];  // init: begin met datum van eerste record.	

	/* dit kan ook in make_ts.py gedaan worden -- scheelt inlaadtijd*/
	total_regio_min=total_regio_max=total_regio[0][varidx];			
	for (i=0; i<total_regio.length;i++) {
		val=total_regio[i][varidx];	
		if ((total_regio_min==null) || (val<total_regio_min)) {total_regio_min=val;}
		if ((total_regio_max==null) || (val>total_regio_max)) {total_regio_max=val;}
		//console.log('chartc:',val,total_regio_min,total_regio_max);
	}
	total_date_min=total_date_max=total_date[0][varidx-1];		
	
	for (i=0; i<total_date.length;i++) {
		val=total_date[i][varidx-1];	
		if ((total_date_min==null) || (val<total_date_min)) {total_date_min=val;}
		if ((total_date_max==null) || (val>total_date_max)) {total_date_max=val;}
	//	console.log('chartc:',val,total_date_min,total_date_max);
	}



	console.log ("prep:",mindate,maxdate); 

	regiosel=data[0][regiocol]; // init: begin met regio van eerste record.

}



function select_data (datesel) {


	start=date_index[datesel].start_row;
	eind=date_index[datesel].eind_row;
	console.log('select_data:',start,eind);
	for (i=start,j=0; i<eind; i++,j++) {
		console.log(data[i][regioidx], data[i][varidx]);
		chart_data.push([ data[i][regioidx], data[i][varidx]]);
	}
}

function init() {

	container = document.getElementById( 'container' );

	camera = new THREE.PerspectiveCamera( 27, window.innerWidth / window.innerHeight, 1, 4000 );
	camera.position.z = 2750;
	scene = new THREE.Scene();

	var light = new THREE.DirectionalLight( 0xffffff, 2 );
	light.position.set( 1, 1, 1 ).normalize();
	scene.add( light );


	mesh={};
	for ( var i = 0; i < xy.length; i ++ ) {
		segment=xy[i];
		var segments = segment.length;;
		var geometry = new THREE.BufferGeometry();
		var material = new THREE.LineBasicMaterial({ vertexColors: true });

		geometry.addAttribute( 'position', Float32Array, segments, 3 );
		geometry.addAttribute( 'color', Float32Array, segments, 3 );

		var positions = geometry.attributes.position.array;
		var colors = geometry.attributes.color.array;

		var r = 1;
		var x,y,z;
		z=0;
	//	console.log(xy);
		w=0;
	
		
		//console.log(segment);
		for (var j=0; j<segment.length; j++ ) {

		//var x = Math.random() * r - r / 2;
		//var y = Math.random() * r - r / 2;
		//var z = Math.random() * r - r / 2;
			var coord=segment[j];
			//console.log(coord);
	//		console.log(coord);
			x=coord[0]*r;
			y=coord[1]*r-0.5*height;
			//console.log('x,y:',x,y);

		// positions

			positions[ w * 3 ] = x;
			positions[ w * 3 + 1 ] = y;
			positions[ w * 3 + 2 ] = z;

		// colors
			colors[ w * 3 ] = 0.5;
			colors[ w * 3 + 1 ] = 0.5;
			colors[ w * 3 + 2 ] = 0.5;
			w+=1;
		}
	

	geometry.computeBoundingSphere();
	mesh[i] = new THREE.Line( geometry, material );
	scene.add( mesh[i] );
	}

    var cube_geometry = new THREE.BoxGeometry( 20, 20, 20 );
//    mincx=centroids[3][0];
//    mincy=centroids[3][1];
    for (var i=0; i<centroids.length; i++) {
    	
    }
	for (var i=0; i<chart_data.length; i++) {
		var record=chart_data[i];
		regio=record[0];
		z=record[1];
		var coord=centroids[regio];
		console.log(z, coord[0],coord[1]);
		

		var object = new THREE.Mesh( cube_geometry, new THREE.MeshLambertMaterial( { color: 0x002c61 } ) );		
		x=coord[0];
		y=coord[1];
		object.position.x = x; //x*1.9-100;
		object.position.y = y-0.5*height; //550-1.2*(8/7)*y;
		object.position.z=0;
		object.scale.x = 1;
		object.scale.y = 1;
		object.scale.z = Math.log(z);
		object.rotation.x = 0/360.0*3.14;
		object.rotation.y = 0/360.0*3.14;;
		object.rotation.z = 0/360.0*3.14;;

		scene.add(object);
	}

	renderer = new THREE.WebGLRenderer( { antialias: false } );
	renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.gammaInput = true;
	renderer.gammaOutput = true;
	renderer.setClearColor(0xEEEEEE, 1.0);
	renderer.sortObjects = false;

	container.appendChild( renderer.domElement );

	controller=new Controller();
	var gui = new dat.GUI();
    var c1=gui.add(controller, 'x').min(0).max(90).step(5);
    var c2=gui.add(controller, 'y').min(0).max(90).step(5);
    var c3=gui.add(controller, 'z').min(0).max(90).step(5);      

    c1.onChange(animate);
    c2.onChange(animate);
    c3.onChange(animate);

	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	container.appendChild( stats.domElement );
	window.addEventListener( 'resize', onWindowResize, false );

}

function onWindowResize() {

	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );

}

//

function animate() {

	requestAnimationFrame( animate );
	render();
	stats.update();
}

function render() {


			
	for ( var i = 0; i < xy.length; i ++ ) {
		mesh[i].rotation.x = controller.x/360.0*3.14; 
		mesh[i].rotation.y = controller.y/360.0*3.14;
		mesh[i].rotation.z = controller.z/360.0*3.14;
	}
	renderer.render( scene, camera );
}







if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var container, stats;
var camera, scene, renderer;
var mesh;

prep_data();
select_data(datesel);
init();
animate();
