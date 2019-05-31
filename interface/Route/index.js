import React from 'react'


export default class Route extends React.Component {
	constructor(props) {
		super(props)

		this.platform = null
		this.map = null
		this.state = {
			app_id: props.app_id,
			app_code: props.app_code,
			center: {
				lat: props.lat,
				lng: props.lng,
			},
			zoom: props.zoom,
			// theme: props.theme,
			// style: props.style,
		}
	}

	componentDidMount() {
		function calculateRouteFromAtoB (platform) {
			let router = platform.getRoutingService(),
			  routeRequestParams = {
				mode: 'fastest;car',
				representation: 'display',
				routeattributes : 'waypoints,summary,shape,legs',
				maneuverattributes: 'direction,action',
				waypoint0: '50.086882,14.4203952', // Brandenburg Gate
				waypoint1: '50.1,14.415'  // Friedrichstraße Railway Station
			  };
		  
		  
			router.calculateRoute(
			  routeRequestParams,
			  onSuccess,
			  onError
			);
		  }
		
		  function onSuccess(result) {
			let route = result.response.route[0];
		   /*
			* The styling of the route response on the map is entirely under the developer's control.
			* A representitive styling can be found the full JS + HTML code of this example
			* in the functions below:
			*/
			addRouteShapeToMap(route);
			addManueversToMap(route);
		  
			// addWaypointsToPanel(route.waypoint);
			// addManueversToPanel(route);
			// addSummaryToPanel(route.summary);
			// // ... etc.
		  }

		  
		  function onError(error) {
			alert('Ooops!');
		  }
		  
		  
		  
		  
		  /**
		   * Boilerplate map initialization code starts below:
		   */
		  
		  // set up containers for the map  + panel
		  let mapContainer = document.getElementById('map'),
			routeInstructionsContainer = document.getElementById('panel');
		  
		  //Step 1: initialize communication with the platform
		  let platform = new window.H.service.Platform({
			app_id: this.props.app_id,
			app_code: this.props.app_code,
			useCIT: true,
			useHTTPS: true
		  });
		  let defaultLayers = platform.createDefaultLayers();

		  //Step 2: initialize a map - this map is centered over Berlin
		  let pixelRatio = window.devicePixelRatio || 1
		  let map = new window.H.Map(mapContainer,
			defaultLayers.normal.xbase,{
			center: this.state.center,
			zoom: 13,
			pixelRatio
		  });
		  
		  //Step 3: make the map interactive
		  // MapEvents enables the event system
		  // Behavior implements default interactions for pan/zoom (also on mobile touch environments)
		  let behavior = new window.H.mapevents.Behavior(new window.H.mapevents.MapEvents(map));
		  
		  // Create the default UI components
		  let ui = window.H.ui.UI.createDefault(map, defaultLayers);
		  
		  // Hold a reference to any infobubble opened
		  let bubble;

		  function openBubble(position, text){
		   if(!bubble){
			  bubble =  new window.H.ui.InfoBubble(
				position,
				// The FO property holds the province name.
				{content: text});
			  ui.addBubble(bubble);
			} else {
			  bubble.setPosition(position);
			  bubble.setContent(text);
			  bubble.open();
			}
		  }
		  

		  function addRouteShapeToMap(route){
			let strip = new window.H.geo.Strip(),
			  routeShape = route.shape,
			  polyline;
		  
			routeShape.forEach(function(point) {
			  let parts = point.split(',');
			  strip.pushLatLngAlt(parts[0], parts[1]);
			});
		  
			polyline = new window.H.map.Polyline(strip, {
			  style: {
				lineWidth: 4,
				strokeColor: 'rgba(0, 128, 255, 0.7)'
			  }
			});
			// Add the polyline to the map
			map.addObject(polyline);
			// And zoom to its bounding rectangle
			map.setViewBounds(polyline.getBounds(), true);
		  }
		  

		  function addManueversToMap(route){
			let svgMarkup = '<svg width="18" height="18" ' +
			  'xmlns="http://www.w3.org/2000/svg">' +
			  '<circle cx="8" cy="8" r="8" ' +
				'fill="#1b468d" stroke="white" stroke-width="1"  />' +
			  '</svg>',
			  dotIcon = new window.H.map.Icon(svgMarkup, {anchor: {x:8, y:8}}),
			  group = new  window.H.map.Group(),
			  i,
			  j;
		  
			// Add a marker for each maneuver
			for (i = 0;  i < route.leg.length; i += 1) {
			  for (j = 0;  j < route.leg[i].maneuver.length; j += 1) {
				// Get the next maneuver.
				let maneuver = route.leg[i].maneuver[j];
				// Add a marker to the maneuvers group
				let marker =  new window.H.map.Marker({
				  lat: maneuver.position.latitude,
				  lng: maneuver.position.longitude} ,
				  {icon: dotIcon});
				marker.instruction = maneuver.instruction;
				group.addObject(marker);
			  }
			}
		  
			group.addEventListener('tap', function (evt) {
			  map.setCenter(evt.target.getPosition());
			  openBubble(
				 evt.target.getPosition(), evt.target.instruction);
			}, false);
		  
			// Add the maneuvers group to the map
			map.addObject(group);
		  }
		  
		  
		//   /**
		//    * Creates a series of window.H.map.Marker points from the route and adds them to the map.
		//    * @param {Object} route  A route as received from the window.H.service.RoutingService
		//    */
		//   function addWaypointsToPanel(waypoints){
		  
		  
		  
		// 	let nodeH3 = document.createElement('h3'),
		// 	  waypointLabels = [],
		// 	  i;
		  
		  
		// 	 for (i = 0;  i < waypoints.length; i += 1) {
		// 	  waypointLabels.push(waypoints[i].label)
		// 	 }
		  
		// 	 nodeH3.textContent = waypointLabels.join(' - ');
		  
		// 	routeInstructionsContainer.innerHTML = '';
		// 	routeInstructionsContainer.appendChild(nodeH3);
		//   }
		  
		//   /**
		//    * Creates a series of window.H.map.Marker points from the route and adds them to the map.
		//    * @param {Object} route  A route as received from the window.H.service.RoutingService
		//    */
		//   function addSummaryToPanel(summary){
		// 	let summaryDiv = document.createElement('div'),
		// 	 content = '';
		// 	 content += '<b>Total distance</b>: ' + summary.distance  + 'm. <br/>';
		// 	 content += '<b>Travel Time</b>: ' + summary.travelTime.toMMSS() + ' (in current traffic)';
		  
		  
		// 	summaryDiv.style.fontSize = 'small';
		// 	summaryDiv.style.marginLeft ='5%';
		// 	summaryDiv.style.marginRight ='5%';
		// 	summaryDiv.innerHTML = content;
		// 	routeInstructionsContainer.appendChild(summaryDiv);
		//   }
		  
		//   /**
		//    * Creates a series of window.H.map.Marker points from the route and adds them to the map.
		//    * @param {Object} route  A route as received from the window.H.service.RoutingService
		//    */
		//   function addManueversToPanel(route){
		  
		  
		  
		// 	let nodeOL = document.createElement('ol'),
		// 	  i,
		// 	  j;
		  
		// 	nodeOL.style.fontSize = 'small';
		// 	nodeOL.style.marginLeft ='5%';
		// 	nodeOL.style.marginRight ='5%';
		// 	nodeOL.className = 'directions';
		  
		// 	   // Add a marker for each maneuver
		// 	for (i = 0;  i < route.leg.length; i += 1) {
		// 	  for (j = 0;  j < route.leg[i].maneuver.length; j += 1) {
		// 		// Get the next maneuver.
		// 		let maneuver = route.leg[i].maneuver[j];
		  
		// 		let li = document.createElement('li'),
		// 		  spanArrow = document.createElement('span'),
		// 		  spanInstruction = document.createElement('span');
		  
		// 		spanArrow.className = 'arrow '  + maneuver.action;
		// 		spanInstruction.innerHTML = maneuver.instruction;
		// 		li.appendChild(spanArrow);
		// 		li.appendChild(spanInstruction);
		  
		// 		nodeOL.appendChild(li);
		// 	  }
		// 	}
		  
		// 	routeInstructionsContainer.appendChild(nodeOL);
		//   }
		  
		  
		//   Number.prototype.toMMSS = function () {
		// 	return  window.Matwindow.H.floor(this / 60)  +' minutes '+ (this % 60)  + ' seconds.';
		//   }
		  
		  // Now use the map as required...
		  calculateRouteFromAtoB (platform);
		
		}

	render() {
		return (
			<div id="map" style={{width: '100%', height: '100vh', background: 'grey'}}></div>
		)
	}
}
