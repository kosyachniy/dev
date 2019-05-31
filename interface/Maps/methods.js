import axios from 'axios'

import api from './api'


// Метки на карте по поиску

export function getGeo(that, data={}) {
	const handlerSuccess = async (other, res) => {
		function addMarkersToMap(map, lat, lng) {
			let parisMarker = new window.H.map.Marker({lat, lng});
			map.addObject(parisMarker);
        }

        function markered(geo) {
            // console.log(geo)
            addMarkersToMap(other.map, geo['Latitude'], geo['Longitude'])
        }

        // let r = []

        for (let i=0; i<res['events'].length; i++) {
            try {
                let el = res['events'][i]
                let elm = await axios.get('https://geocoder.cit.api.here.com/6.2/geocode.json?searchtext=' + el['location'] + '&app_id=qa0WJfBASLFPiWJIm8zA&app_code=CSg50IevfYpGuIaHzNjj_Q&gen=8')
                let geo = JSON.parse(elm['request']['response'])['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']

                res['events'][i]['geo'] = {
                    'lant': geo['Latitude'],
                    'long': geo['Longitude'],
                }
                // console.log(res['events'][i]['geo'])
                // r.push(geo)

                markered(geo)
                // console.log(res['events'])
            }
            catch (err) {
                console.error(err)
            }
        }

        // other.props.markers = JSON.stringify(res['events'])
        other.setState({markers: JSON.stringify(res['events'])})

        // res['events'].map(el => {
        //     axios.get('https://geocoder.cit.api.here.com/6.2/geocode.json?searchtext=' + el['location'] + '&app_id=qa0WJfBASLFPiWJIm8zA&app_code=CSg50IevfYpGuIaHzNjj_Q&gen=8').then(elm => {
        //         try {
        //             let geo = JSON.parse(elm['request']['response'])['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
        //             markered(geo)
        //             el['geo'] = geo
        //         } catch {
        //         }
               
        //     })
        // })
        
        // // 
	}

	api(that, 'get', data, handlerSuccess)
}
