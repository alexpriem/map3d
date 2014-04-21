
function init() {

	container = document.getElementById( 'container' );

	camera = new THREE.PerspectiveCamera( 27, window.innerWidth / window.innerHeight, 1, 4000 );
	camera.position.z = 2750;
	scene = new THREE.Scene();

	var segments = total_length;
	var geometry = new THREE.BufferGeometry();
	var material = new THREE.LineBasicMaterial({ vertexColors: true });

	geometry.addAttribute( 'position', Float32Array, segments, 3 );
	geometry.addAttribute( 'color', Float32Array, segments, 3 );

	var positions = geometry.attributes.position.array;
	var colors = geometry.attributes.color.array;

	var r = 800;
	var x,y,z;
	z=0;
//	console.log(xy);
	w=0;
	for ( var i = 0; i < xy.length; i ++ ) {
		segment=xy[i];
		//console.log(segment);
		for (var j=0; j<segment.length; j++ ) {

		//var x = Math.random() * r - r / 2;
		//var y = Math.random() * r - r / 2;
		//var z = Math.random() * r - r / 2;
			var coord=segment[j];
			//console.log(coord);
	//		console.log(coord);
			x=(coord[0]-minx)/dx*500;
			y=(coord[1]-miny)/dy*500;
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
	}

	geometry.computeBoundingSphere();
	mesh = new THREE.Line( geometry, material );
	scene.add( mesh );

	renderer = new THREE.WebGLRenderer( { antialias: false } );
	renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.gammaInput = true;
	renderer.gammaOutput = true;

	container.appendChild( renderer.domElement );

	//

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

	//var time = Date.now() * 0.001;

	//mesh.rotation.x = time * 0.25;
	//mesh.rotation.y = time * 0.5;
	renderer.render( scene, camera );
}







if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var container, stats;
var camera, scene, renderer;
var mesh;

init();
animate();
