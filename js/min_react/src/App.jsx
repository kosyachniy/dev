import React, { useState, useEffect } from 'react'

import api from './lib/api'


const App = () => {
    const [posts, setPosts] = useState([])

    useEffect(() => {
        api('posts.get', {}).then(
            res => setPosts(res['posts'])
        )
    }, [])

    return (
        <>
            { JSON.stringify(posts) }
        </>
    )
}

export default App;
