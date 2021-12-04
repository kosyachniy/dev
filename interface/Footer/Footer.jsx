import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import './style.css'
import { name, mail, phone, social } from '../../../sets'


const Footer = (props) => {
    const { system, changeLang } = props
    const { t } = useTranslation()

    return (
        <footer className={`section footer-classic context-${system.theme} bg-${system.theme}`}>
            <div className="container">
                <div className="row row-30">
                    <div className="col-md-4 col-xl-5">
                        <div className="pr-xl-4">
                            <p><Link to="/" className="brand"><img src={`/brand/logo_${system.color}.svg`} alt={ name } /></Link></p>
                            <p>{ t('brand.description') }</p>
                            <p className="rights"><span>{ name }</span><span> </span><span>©</span><span> </span><span className="copyright-year">2018-{ new Date().getFullYear() }</span></p>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <h5>{ t('footer.contacts') }</h5>
                        <dl className="contact-list">
                            <dt>{ t('footer.address') }</dt>
                            <dd>{ t('brand.address') }</dd>
                        </dl>
                        <dl className="contact-list">
                            <dt>{ t('footer.mail') }</dt>
                            <dd><a href={ 'mailto:' + mail }>{ mail }</a></dd>
                        </dl>
                        <dl className="contact-list">
                            <dt>{ t('footer.phone') }</dt>
                            <dd><a href={ 'tel:' + phone }>{ phone }</a></dd>
                        </dl>
                    </div>
                    <div className="col-md-4 col-xl-3">
                        <h5>{ t('footer.links') }</h5>
                        <ul className="nav-list">
                            <li><Link to="/about/">{ t('footer.about') }</Link></li>
                            <li><Link to="/feedback/">{ t('footer.feedback') }</Link></li>
                            <li><Link to="/codex/">{ t('footer.rules') }</Link></li>
                        </ul>
                        <span className="badge" onClick={ () => {changeLang('en')} }><img src="/lang/en.svg" alt="en" /></span>
                        <span className="badge" onClick={ () => {changeLang('ru')} }><img src="/lang/ru.svg" alt="ru" /></span>
                        <br />
                        <div className="social">
                            { social.map((el, num) =>
                                <a href={ el.data } key={ num }><span className="badge"><img src={ '/social/' + el.title + '.ico' } alt={ el.title } /></span></a>
                            ) }
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    )
}

export default Footer;
