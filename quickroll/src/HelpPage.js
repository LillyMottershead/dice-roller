import React from 'react';
import './App.css';

function Help(props) {
    if (!props.show) {
        return null;
    }
    return (
        <div className='panel' style={{textAlign: 'left'}}>
            <QuickStart />
        </div>
    )
}

function QuickStart(props) {
    return (
        <section className='textheavy'>
            <h3>Quick Start</h3>
            <p>
                Hello, welcome to QuickRoll! Most functionallity is available through the command line at the top of the Roller page. Try typing <code>d20</code>!
                Now try making the roll more complicated with <code>2d10+d4+7</code>.
                If you wanted to make that roll three more times, you can type <code>3</code> in the adjacent text input. And if you want to clear the rolls that you currently see, type <code>clear</code>, or you can directly click on the rolls that you want to have removed.
            </p>
            <p>
                If you wanted to have advantage or disadvantage, you have two options. You could use the dice notation itself, as in <code>2d20k1</code> for advantage(<code>k1</code> means to keep the 1st highest dice roll), or <code>2d20kl1</code> for disadvantage (the <code>l</code> tells the keep notation to only keep the lowest). An alternative way would be to use the <code>adv</code> and <code>dis</code> keywords: <code>d20 adv</code>. Another useful keyword you can use on pure rolls would be <code>max</code>, which maxes the output of all dice rolls.
            </p>
            <p>
                The last major thing you can do with these pure rolls is label them. If you wanted to note the kind of damage or the source, you can create one with square brackets: <code>6d6 [fire]</code>.
            </p>
            <p>
                If you want to save a particular roll so that you can use it numerous times later, you can create an alias with 
            </p>
            <center>
                <code>alias &lt;name&gt; &#123;roll 1&#125; &#123;roll 2&#125; &#123;roll 3&#125; ...</code>
            </center>
            <p>
                Note, alias names cannot contain white space. For example <code>alias fireball &#123;8d6 [fire]&#125;</code>. To use the alias simply enter <code>fireball</code>, or click on it in the list of aliases. Another example might be 
            </p>
            <center>
                <code>alias shortsword &#123;d20 [to hit]&#125; &#123;d6 [slashing]&#125;</code>
            </center>
            <p>
                Like pure rolls, it is easy to give this attack alias advantage or disadvantage with <code>shortsword dis</code>. This will assume that the d20 to hit roll is the first roll. You can also add an additional roll to a single use of the alias by doing <code>shortsword &#123;d4+1 [poison]&#125;</code>.
            </p>
            <p>
                QuickRoll also has crit handling (you can pick which crit damage rule you prefer in the settings page). In order to do so, however, you need to indicate which rolls of an alias are the 'to hit' rolls, and which rolls are eligible for crit damage. Using the shortsword example from before, this can be done in two ways. You can use <code>tohit</code> and <code>cancrit</code> on individual rolls: 
            </p>
            <center>
                <code>alias shortsword &#123;d20 [to hit] tohit&#125; &#123;d6 [slashing] cancrit&#125;</code>
            </center>
            <p>
                or as a shorthand, you can use the alias specific <code>attack</code> keyword. This keyword assumes that the first roll is the to hit roll, and all following are crit damage.
            </p>
            <center>
                <code>alias shortsword &#123;d20 [to hit]&#125; &#123;d6 [slashing]&#125; attack</code>
            </center>
            <p>
                Now, whenever the to hit roll is 20, crit damage will be automatically calculated! If you want to see the math, you can always mouseover the individual rolls for a helpful tooltip. With these rules, most rolls in DnD will be easy to make, and when necessary, store and use repeatedly using the alias system. Good luck!
            </p>
        </section>
    );
}

export default Help;