import React from 'react'
import {render} from 'react-dom'

import App from './components/App'

const domContainer = document.querySelector('#root');
render(<App />, domContainer)