import { serverSideTranslations } from 'next-i18next/serverSideTranslations'

import Map from '../../components/Map'


export default () => {
    // componentWillMount() {
    //     this.setState({pet: document.location.search.split('&')[0].split('=').pop()});
    // }

    return (
        <div id="map">
            <div>
                <Map />
            </div>
        </div>
    )
}

export const getStaticProps = async ({ locale }) => ({
    props: {
        ...await serverSideTranslations(locale, ['common']),
    },
})
