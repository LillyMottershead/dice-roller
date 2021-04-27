import React from 'react';
import './App.css';
import command from './roll.js';

class App extends React.Component {
    constructor(props) {
        super(props);
        if (!localStorage.aliases) {
            localStorage.setItem('aliases', JSON.stringify({}))
        }
    }
    
    render() {
        return (
            <section>
                <h1>quickroll</h1>
                <button className='input' onClick={this.onSettingsClick}>settings</button>
                <Main />
            </section>
        )
    }
}

class Main extends React.Component {
    constructor(props) {
        super(props);
        if (!localStorage.aliases) {
            localStorage.setItem('aliases', JSON.stringify({}))
        }
        this.state = {
            rollCommand: '',
            times: '',
            output: '',
            aliases: JSON.parse(localStorage.aliases || '{}'),
            log: { components: [], currKey: 0 },
        };
        this.textInputRef = React.createRef();
        this.onSubmit = this.onSubmit.bind(this);
        this.onRollFormChange = this.onRollFormChange.bind(this);
        this.onLogClear = this.onLogClear.bind(this);
    }
    
    onRollFormChange = (e => {
        const target = e.target;
        const value = target.value;
        const name = target.name;
        this.setState({ [name]: value });
    });
    onLogClear = (e => {
        e.preventDefault();
        this.setState({ log: {components: [], currKey: 0}});
    });
    onSubmit = (e => {
        e.preventDefault();
        function getRolls(rollCommand, index, log) {
            function pushToLog(log, message) {
                if (log.components.length > 100) {
                    log.components.pop();
                }
                log.components.unshift(<p key={`log#${log.currKey++}`}>{message}</p>);
                log.currKey %= 101
            }
            let output;
            try {
                output = command(rollCommand);
                pushToLog(log, output.message);
                if (output.rolls) {
                    output.rolls.forEach(x => {
                        if (x.critString) {
                            pushToLog(log, `${x.fullString}, ${x.critString}, ${x.result} ${x.label}`);
                        } else {
                            pushToLog(log, `${x.fullString} ${x.label}`);
                        }
                    });
                    output = output.rolls.map((x, i) => <Roll key={`roll#${i}`} roll={x} />);
                } else {
                    output = <div className='flex-child'>{output.message}</div>;
                }
            } catch (err) {
                pushToLog(log, err.message);
                output = err.message;
            }
            return <Call key={`call#${index}`} rolls={output} />
        }
        if (this.state.rollCommand === 'clear') {
            this.onLogClear(e);
            this.setState({
                rollCommand: '',
                times: '',
                output: '',
            });
        } else if (this.state.rollCommand !== '') {
            let times = +this.state.times || 1;
            let output = [...new Array(times).keys()].map((x, i) => getRolls(this.state.rollCommand, i, this.state.log));
            this.setState({
                rollCommand: '',
                times: '',
                output: output,
                aliases: JSON.parse(localStorage.aliases || '{}'),
                log: this.state.log,
            });
        }
        this.textInputRef.current.focus();
    });

    render() {
        return (
            <section>
                    <RollForm
                        rollCommand={this.state.rollCommand}
                        times={this.state.times}
                        onRollFormChange={this.onRollFormChange}
                        onSubmit={this.onSubmit}
                        textInputRef={this.textInputRef} />
                    <section className='h-container'>
                        {this.state.output}
                    </section>
                    <section className='h-container'>
                        <Aliases aliases={this.state.aliases} handleUpload={this.handleUpload} />
                        <Log log={this.state.log.components} onLogClear={this.onLogClear} />
                    </section>
            </section>
    )}
}

class RollForm extends React.Component {
    render() {
        return (
            <form>
                <input className='input-text' type="text" ref={this.props.textInputRef} autoFocus name="rollCommand" value={this.props.rollCommand} onChange={this.props.onRollFormChange} />
                <input className='input-text' type="text" style={{ width: '30px' }} name="times" value={this.props.times} onChange={this.props.onRollFormChange} />
                <input className='input' type="submit" value=">" onClick={this.props.onSubmit} />
            </form>
        );
    };
}

class Call extends React.Component {
    render() {
        return (
            <section className='h-container flex-child' style={{ border: 'none', margin: '10px', maxWidth: '30%' }}>
                {this.props.rolls}
            </section>
        )
    }
}

class Roll extends React.Component {
    render() {
        let res = this.props.roll.result + (this.props.roll.critResult || 0);
        let label = this.props.roll.label || '';
        let fullString = this.props.roll.fullString || '';
        let critString = this.props.roll.critString || '';
        let dice = this.props.roll.dice.map((x, i) => <DieImage key={`rollImage#${i}}`} die={x} />);
        return (
            <div className='flex-child tooltip' style={{ 'margin': '-1px', 'marginBottom': '0px' }}>
                {dice}
                <p>{res}<span style={{ fontSize: '.75em' }}> {label}</span></p>
                <span className='tooltiptext'>{fullString}<br />{critString}</span>
            </div>
        );
    }
}

class DieImage extends React.Component {
    render() {
        let fileName = process.env.PUBLIC_URL;
        let colorOrGray = this.props.die.kept ? 'dice/' : 'gray_dice/';
        let sides = this.props.die.sides;
        let result = this.props.die.num;
        fileName = `${fileName}/${colorOrGray}d${sides}_${result}.svg`;
        return (
            <img src={fileName} alt={`${result} (d${sides})`} height='50px' />
        );
    }
}

class Aliases extends React.Component {
    render() {
        let aliases = Object.keys(this.props.aliases);
        aliases.sort();
        aliases = aliases.map((x, i) => <p key={`alias#${i}`}>{x}</p>);
        return (
            <div className='flex-child aliases'>
                <form style={{ padding: '5px' }}>
                    <label className='h2'>Aliases</label>
                </form>
                <div>
                    {aliases}
                </div>
            </div>
        );
    }
}

class Log extends React.Component {
    render() {
        return (
            <div className='flex-child log'>
                <label className='h2'>
                    Log
                  <button className='input' onClick={this.props.onLogClear}>Clear</button>
                </label>
                <div className='inner-log'>
                    {this.props.log}
                </div>
            </div>
        );
    }
}

export default App;
