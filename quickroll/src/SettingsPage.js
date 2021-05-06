import React from 'react';
import './App.css';

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
            <div>
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
            </div>
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

export default Settings;