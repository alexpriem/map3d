
var controller;

var Controller =function () {

	this.x=0;
	this.y=0;
	this.z=0;
};

function init() {

	container = document.getElementById( 'container' );

	camera = new THREE.PerspectiveCamera( 27, window.innerWidth / window.innerHeight, 1, 4000 );
	camera.position.z = 2750;
	scene = new THREE.Scene();


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

		var r = 1000;
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
			x=(coord[0]-minx)/dx*r;
			y=(coord[1]-miny)/dy*r*(8/7)-500;
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

	renderer = new THREE.WebGLRenderer( { antialias: false } );
	renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.gammaInput = true;
	renderer.gammaOutput = true;
	renderer.setClearColor(0xEEEEEE, 1.0);

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

init();
animate();
