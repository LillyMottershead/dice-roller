import React from 'react';
import './App.css';
import Roller from './RollerPage.js';
import Settings from './SettingsPage.js';
import Help from './HelpPage.js';


class App extends React.Component {
    constructor(props) {
        super(props);
        if (!localStorage.aliases) {
            localStorage.setItem('aliases', JSON.stringify({}));
        }
        if (!localStorage.settings) {
            localStorage.setItem('settings', JSON.stringify({critRule: 'rolldouble'}));
        }
        this.state = {
            page: 'roller',
            settings: JSON.parse(localStorage.settings),
        };
        this.onPageClick = this.onPageClick.bind(this);
        this.onSettingsChange = this.onSettingsChange.bind(this);
    }

    onPageClick(e) {
        this.setState({
            page: e.target.name,
        });
    }
    onSettingsChange(e) {
        let settings = this.state.settings;
        settings[e.target.name] = e.target.value;
        this.setState({
            settings: settings,
        });
        localStorage.setItem('settings', JSON.stringify(settings));
    }

    render() {
        let pages = ['roller', 'settings', 'help'];
        function pageButton(name, onPageClick, active) {
            return (
            <button className={active? 'page-button-active' : 'page-button'} name={name} onClick={onPageClick} active>
                {`${name.charAt(0).toUpperCase()}${name.slice(1)}`}
            </button>
            );
        }
        let pageButtons = pages.map(x => pageButton(x, this.onPageClick, x === this.state.page));
        return (
            <div>
                <h1 style={{ padding: '10px' }}> quickroll </h1>
                <span style={{ padding: '10px' }}>
                    {pageButtons}
                </span>
                <Roller show={this.state.page === 'roller'} settings={this.state.settings}/>
                <Settings show={this.state.page === 'settings'} settings={this.state.settings} onSettingsChange={this.onSettingsChange}/>
                <Help show={this.state.page === 'help'}/>
            </div>
        );
    }
}

export default App;
