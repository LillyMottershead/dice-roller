import React from 'react';
import './App.css';
import command from './roll.js';

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
            page: 'settings',
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
        return (
            <section>
                <h1> quickroll </h1>
                <span>
                    <button className='panel input' name='roller' onClick={this.onPageClick}>
                        Roller
                    </button>
                    <button className='panel input' name='settings' onClick={this.onPageClick}>
                        Settings
                    </button>
                </span>
                <Main show={this.state.page === 'roller'} settings={this.state.settings}/>
                <Settings show={this.state.page === 'settings'} settings={this.state.settings} onSettingsChange={this.onSettingsChange}/>
            </section>
        );
    }
}

class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rollCommand: '',
            times: '',
            output: { calls: [], currKey: 0},
            aliases: JSON.parse(localStorage.aliases || '{ }'),
            log: { components: [], currKey: 0 },
        };
        this.textInputRef = React.createRef();
        this.onSubmit = this.onSubmit.bind(this);
        this.onRollFormChange = this.onRollFormChange.bind(this);
        this.onLogClear = this.onLogClear.bind(this);
    }

    onRollFormChange = e => {
        const target = e.target;
        const value = target.value;
        const name = target.name;
        this.setState({ [name]: value, });
    };
    onLogClear = e => {
        e.preventDefault();
        this.setState({ log: { components: [], currKey: 0 } });
    };
    onSubmit = e => {
        e.preventDefault();

        function getRolls(rollCommand, index, log, critRule) {
            function pushToLog(log, message) {
                if (log.components.length > 100) {
                    log.components.pop();
                }
                log.components.unshift(<p key={`log#${log.currKey++}`}> {message} </p>);
                log.currKey %= 101;
            }
            let output;
            try {
                output = command(rollCommand, critRule);
                pushToLog(log, output.message);
                if (output.rolls) {
                    output.rolls.forEach(x => {
                        let message;
                        if (x.critString) {
                            message = `${x.fullString}, ${x.critString}, ${x.result} ${x.label}`;
                        } else {
                            message = `${x.fullString} ${x.label}`
                        }
                        pushToLog(log, message);
                    });
                    output = output.rolls.map((x, i) => <Roll key={`roll#${i}`} roll={x} />);
                } else {
                    output = <div className='panel flex-child'> {output.message} </div>;
                }
            } catch (err) {
                pushToLog(log, err.message);
                output = <div className='panel flex-child'> {err.message} </div>;
            }
            return <Call key={`call#${index}`} rolls={output} />;
        }
        if (this.state.rollCommand === 'clear') {
            this.setState({
                rollCommand: '',
                times: '',
                output: {calls: [], currKey: 0},
            });
        } else if (this.state.rollCommand === 'clear log') {
            this.onLogClear(e);
            this.setState({
                rollCommand: '',
                times: '',
            });
        } else if (this.state.rollCommand !== '') {
            let times = +this.state.times || 1;
            let newOutput = [...new Array(times).keys()].map((x, i) =>
                getRolls(this.state.rollCommand, this.state.output.currKey + i, this.state.log, this.props.settings.critRule)
            );
            this.setState({
                rollCommand: '',
                times: '',
                output: {calls: [...this.state.output.calls, ...newOutput], currKey: this.state.output.currKey + newOutput.length},
                aliases: JSON.parse(localStorage.aliases || '{ }'),
                log: this.state.log,
            });
        }
        this.textInputRef.current.focus();
    };

    render() {
        if (!this.props.show) {
            return null;
        }
        return (
            <section>
                <RollForm
                    rollCommand={this.state.rollCommand}
                    times={this.state.times}
                    onRollFormChange={this.onRollFormChange}
                    onSubmit={this.onSubmit}
                    textInputRef={this.textInputRef}
                />
                <section className='h-container'> {this.state.output.calls} </section>
                <section className='h-container'>
                    <Aliases
                        aliases={this.state.aliases}
                        handleUpload={this.handleUpload}
                    />
                    <Log log={this.state.log.components} onLogClear={this.onLogClear} />
                </section>
            </section>
        );
    }
}

class Settings extends React.Component {
    render() {
        if (!this.props.show) {
            return null;
        }
        function critRuleRadioButton(value, content, props) {
            return (
                <RadioButton 
                    name='critRule'
                    value={ value } 
                    onChange={ props.onSettingsChange }
                    content={ content }
                    checked={ props.settings.critRule === value }
                />
            );
        }
        return (
            <section>
                <div className='panel' style={{ textAlign: 'left' }}>
                    <h2 style={{ textAlign: 'center'}}> Settings </h2>
                    <h3> Crit Rule </h3>
                    <i style={{ fontSize: '.75em' }}>Note that this only applies to future rolls.</i>
                    <form style={{ paddingTop: '.75em'}}>
                        { critRuleRadioButton('rolldouble', 'Roll double the number of dice.', this.props) }<br />
                        { critRuleRadioButton('doubledice', 'Roll the dice normally and double them.', this.props) }<br />
                        { critRuleRadioButton('addmaxdice', 'Roll the dice normally and add the maximum possible dice roll on top.', this.props) }<br />
                    </form>
                </div>
            </section>
        );
    }
}

function RadioButton(props) {
    return (
        <label className='input-radio-container'>
            <input 
                type='radio'
                name={props.name}
                value={props.value}
                onChange={props.onChange}
                checked={props.checked}
            />
            <span className='input-radio-check'></span>
            {props.content}
        </label>
    );
}

function RollForm(props) {
    return (
        <form style={{ margin: '10px', }}>
            <input
                className='panel input-text'
                type='text'
                ref={props.textInputRef}
                autoFocus
                name='rollCommand'
                value={props.rollCommand}
                onChange={props.onRollFormChange}
            />
            <input
                className='panel input-text'
                type='text'
                style={{ width: '30px' }}
                name='times'
                value={props.times}
                onChange={props.onRollFormChange}
            />
            <input
                className='panel input'
                type='submit'
                value='>'
                onClick={props.onSubmit}
            />
        </form>
    );
}

function Call(props) {
    return (
        <section
            className='h-container flex-child'
            style={{ border: 'none', margin: '10px', maxWidth: '30%' }}
        >
            {props.rolls}
        </section>
    );
}

function Roll(props) {
    let res = props.roll.result + (props.roll.critResult || 0);
    let label = props.roll.label || '';
    let fullString = props.roll.fullString || '';
    let critString = props.roll.critString || '';
    let dice = props.roll.dice.map((x, i) => <DieImage key={`rollImage#${i}}`} die={x} />);
    return (
        <div
            className='panel flex-child tooltip'
            style={{ margin: '-1px', marginBottom: '0px' }}
        >
            {dice}
            <p>
                {res} <span style={{ fontSize: '.75em' }}> {label} </span>
            </p>
            <span className='tooltiptext'>
                {fullString} <br /> {critString}
            </span>
        </div>
    );
}

function DieImage(props) {
    let fileName = process.env.PUBLIC_URL;
    let colorOrGray = props.die.kept ? 'dice/' : 'gray_dice/';
    let sides = props.die.sides;
    let result = props.die.num;
    fileName = `${fileName}/${colorOrGray}d${sides}_${result}.svg`;
    return <img src={fileName} alt={`${result} (d${sides})`} height='50px' />;
}

function Aliases(props) {
    let aliases = Object.keys(props.aliases);
    aliases.sort();
    aliases = aliases.map((x, i) => <p key={`alias#${i}`}> {x} </p>);
    return (
        <div className='panel flex-child aliases'>
            <form style={{ padding: '5px' }}>
                <label className='h2'> Aliases </label>
            </form>
            <div> {aliases} </div>
        </div>
    );
}

function Log(props) {
    return (
        <div className='panel log'>
            <h2>
                Log
                <button className='panel input' onClick={props.onLogClear}>
                    Clear
                </button>
            </h2>
            <div className='inner-log'>
                {props.log}
            </div>
        </div>
    );
}

export default App;
