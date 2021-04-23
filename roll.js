"use strict"

// Reducer for Array.reduce() that sums all elements in aray
const sumReducer = (accumulator, currentValue) => accumulator + currentValue;

// Regex patterns
const singleRollCapturingPattern = /^(\d+)?d(\d+)(?:k([l-])?(\d+))?$/;
const whitespacePattern = /\s+/;
const compoundRollPattern = /^(?:(?:(?:\d+)?d\d+(?:k(?:[l-])?\d+)?)|[+\-*/()]|\d+|\s+)+$/;
const compoundRollTokensPattern = /((?:\d+)?d\d+(?:k(?:[l-])?\d+)?)|([+\-*/()])|(\d+)/g;
const labelPattern = /\[(.*?)\]/g;
const aliasRollPattern = /\{(.*?)\}/g;
const argPattern = /(?:(\w+)(?:\((.*?)\))?)/g;

const argNameToFunction = {
    'add': add,
    'replace': replace,
    'adv': (compRoll) => replace(compRoll, 'd20', '2d20k1'),
    'dis': (compRoll) => replace(compRoll, 'd20', '2d20kl1'),
    'max': (compRoll) => compRoll.max = true,
    'tohit': (compRoll, minToCrit = 20) => {
        compRoll.tohit = true;
        compRoll.minToCrit = minToCrit;
    },
    'cancrit': (compRoll) => compRoll.cancrit = true,
    'crit': (compRoll) => compRoll.crit = true,
}

/**
 * @param {string} str - String to test for being in single roll notation 
 * @returns {boolean} - True if the str is a single roll, false otherwise
 */
function isSingleRoll(str) {
    return str.match(singleRollCapturingPattern) != undefined;
}

/**
 * @param {string} str - The roll string 
 * @param {boolean} isMax - True if dice should give max results, false otherwise
 * @returns 
 */
function singleRoll(str, isMax=false) {
    let match = str.match(singleRollCapturingPattern);
    if (!match) {
        throw `Cannot parse ${str} as a valid roll.`;
    }
    const sides = +match[2], times = +match[1] || 1, keep = +match[4] || 0, keepHighest = !match[3];
    if (sides < 2) {
        throw `Less than 2 sides in ${str}`;
    }
    if (times < 1) {
        throw `Rolling less than 1 time in ${str}`;
    }
    if (keep < 0) {
        throw `Cannot keep less 1 die in ${str}`;
    }
    if (keep > times) {
        throw `Cannot keep more die than are rolled in ${str}`;
    }
    let keepNotation = keep? `k${keepHighest? '' : 'l'}${keep}` : '';
    const notation = `${times}d${sides}${keepNotation}`;
    
    const rolls = [];
    for (let i = 0; i < times; i++) {
        rolls.push({
            sides,
            num: isMax? sides : Math.ceil(Math.random() * sides),
            kept: true,
        });
    }
    if (keep < times) {
        let discardedRolls = [...rolls];
        discardedRolls.sort((a, b) => a.num - b.num);
        if (!keepHighest) {
            discardedRolls.reverse();
        }
        discardedRolls.slice(0, keep).forEach(roll => roll.kept = false);
    }
    let keptRolls = rolls.filter(roll => roll.kept).map(roll => roll.num);
    let result = keptRolls.reduce(sumReducer);
    return {
        sides,
        result,
        rolls,
        desc: `${notation} (${rolls.map(roll => roll.num).join(', ')})`,
    };
}

/**
 * @param {Object} compRoll - The compound roll object
 * @param {string} extra - The extra roll string that should be added to the roll
 */
function add(compRoll, extra) {
    let extraTokens = extra.match(compoundRollTokensPattern);
    if (!'+-*/'.includes(extraTokens[0])) {
        compRoll.tokens.push('+');
    }
    compRoll.tokens.push(...extraTokens);
}

/**
 * @param {Object} compRoll - The compound roll object 
 * @param {string} target - The target compound roll token that should be replaced 
 * @param {string} repl - The replacement token
 */
function replace(compRoll, target, repl) {
    let index = compRoll.tokens.indexOf(target);
    if (index != -1) {
        compRoll.tokens[compRoll.tokens.indexOf(target)] = repl;
    }
}


/**
 * @param {string} str - The compound roll string 
 * @param {boolean} crit - Whether or not the roll should have a crit bonus calculation
 * @param {string} critRule - The rule for crits, either 'rolldouble', 'doubledice', or 'addmaxdice'
 * @returns 
 */
function compoundRoll(str, crit=false, critRule='addmaxdice') {
    let res = {crit,};
    
    // set label and remove from str
    res.label = Array.from(str.matchAll(labelPattern), x => x[1])[0] || '';
    str = str.replaceAll(labelPattern, '');
    
    // get arguments and remove from str
    let args = Array.from(str.matchAll(argPattern));
    args = args.filter(a => !a[0].match(compoundRollPattern));
    args.reverse();
    args.forEach(x => {
        str = `${str.slice(0,x.index)}${str.slice(x.index+x[0].length)}`;
    });
    args.reverse();
    args = args.map(x => {
        let arr = {name: x[1]};
        arr.params = (x[2])? x[2].split(/\s*,\s*/) : [];
        return arr;
    });
    
    // tokenize str into compound roll tokens
    if (!str.match(compoundRollPattern)) {
        throw `Unknown command.`
    }
    res.tokens = str.match(compoundRollTokensPattern);

    // apply arguments
    for (let arg of args) {
        if (argNameToFunction[arg.name]) {
            argNameToFunction[arg.name](res, ...arg.params);
        }
    }

    let tokensWithRolls = res.tokens.map(token => isSingleRoll(token)? singleRoll(token, res.max || false) : token);
    res.dice = tokensWithRolls.filter(token => token.desc != undefined);
    res.dice = [].concat(...res.dice.map(x => x.rolls))
    res.desc = tokensWithRolls.map(token => token.desc || token).join(' ');
    let tokensEvaluated = tokensWithRolls.map(token => token.result || token).join(' ');
    res.result = Function(`"use strict";return ${tokensEvaluated};`)();

    if (res.tohit) {
        res.crit = tokensWithRolls.find(token => token.sides == 20).result >= res.minToCrit || res.crit;
    }

    if (res.crit && res.cancrit) {
        function rollDouble(max=false) {
            let extraRolls = res.tokens.filter(token => isSingleRoll(token));
            extraRolls = extraRolls.map(token => singleRoll(token, max));
            res.critDesc = extraRolls.map(token => token.desc).join(' + ');
            res.critResult = extraRolls.map(token => token.result).reduce(sumReducer);
        }
        if (critRule == 'rolldouble') {
            rollDouble();
        } else if (critRule == 'doubledice') {
            let rolls = tokensWithRolls.filter(token => (typeof token) == 'object');
            res.critDesc = rolls.map(token => token.desc).join(' + ');
            res.critResult = rolls.map(token => token.result).reduce(sumReducer);
        } else if (critRule == 'addmaxdice') {
            rollDouble(true);
        }
        res.fullString =  `${res.desc} = ${res.result}`;
        res.critString = `CRIT: ${res.critDesc} = ${res.critResult}`;
    } else {
        res.fullString = `${res.desc} = ${res.result}`;
    }
    return res;
}


function aliasArgs(rolls, argsString) {
    let args = Array.from(argsString.matchAll(argPattern));
    args = args.map(x => {
        let arr = {name: x[1]};
        arr.params = (x[2])? x[2].split(/\s*,\s*/) : [];
        return arr;
    });

    for (let arg of args) {
        if (arg.name == 'attack') {
            rolls[0] = rolls[0].concat(' tohit');
            let cancrit = arg.params;
            if (cancrit.length == 0) {
                cancrit = [...new Array(rolls.length).keys()].slice(1);
            }
            cancrit.forEach(x => rolls[x] = rolls[x].concat(' cancrit'));
        } else if (Object.keys(argNameToFunction).includes(arg.name)) {
            let argFunction = argNameToFunction[arg.name];
            let rollIndex;
            if (arg.params.length == argFunction.length - 1) {
                rollIndex = 0;
            } else {
                rollIndex = +arg.params[arg.params.length - 1] - 1;
                arg.params = arg.params.slice(0, arg.params.length);
            }
            arg = `${arg.name}(${arg.params.join(',')})`;
            rolls[rollIndex] = rolls[rollIndex].concat(' ', arg);
        } else {
            throw `Unrecognized argument ${arg.name}`;
        }
    }
}


function deleteCommand(tokens) {
    const aliases = JSON.parse(localStorage.aliases);
    if (tokens.length < 1) {
        throw `Missing target alias to delete.`;
    }
    const targetAlias = tokens[0];
    if (!aliases[targetAlias]) {
        throw `Alias ${targetAlias} does not exist.`;
    }
    delete aliases[targetAlias];
    localStorage.setItem('aliases', JSON.stringify(aliases));
    return {message: `Removed ${targetAlias} from list of aliases.`, alias: targetAlias};
}


function aliasCommand(tokens) {
    const aliases = JSON.parse(localStorage.aliases);
    function listAliases() {
        const aliases = JSON.parse(localStorage.aliases);
        if (Object.keys(aliases).length === 0) {
            return {message: `No aliases.`};
        }
        return {message: `Aliases: ${Object.keys(aliases).join(', ')}`,};
    }
    if (tokens.length < 1) {
        return listAliases();
    }
    let frontToken = tokens[0];
    tokens = tokens.slice(1);
    if (frontToken === 'delete') {
        return deleteCommand(tokens);
    } 
    if (frontToken === 'list') {
        return listAliases();
    }
    if (tokens.length < 1) {
        if (!aliases[frontToken]) {
            throw `Alias ${frontToken} does not exist.`;
        }
        return {message: `${frontToken}: ${aliases[frontToken].rolls.join(', ')}`};
    }
    let aliasCode = tokens.join(' ');
    aliases[frontToken] = {rolls: Array.from(aliasCode.matchAll(aliasRollPattern), x => x[1])};
    aliasCode = aliasCode.replaceAll(aliasRollPattern, '');
    aliasArgs(aliases[frontToken].rolls, aliasCode);
    localStorage.setItem('aliases', JSON.stringify(aliases));
    return {message: `Added ${frontToken} to aliases.`, alias: frontToken};
}


function callAlias(alias, argsString) {
    let rolls = JSON.parse(localStorage.aliases)[alias].rolls;
    // add any extra rolls
    rolls = rolls.concat(Array.from(argsString.matchAll(aliasRollPattern), x => x[1]));
    aliasArgs(rolls, argsString);
    let crit = false;
    rolls = rolls.map(x => {
        let roll = compoundRoll(x, crit);
        crit = roll.crit || crit;
        return roll;
    });
    return {
        message: `Calling ${alias}:`,
        rolls,
    };
}


function command(str) {
    let tokens = str.split(whitespacePattern);
    if (tokens.length < 1) {
        return `empty command.`;
    }
    
    let frontToken = tokens[0];
    tokens = tokens.slice(1);
    if (frontToken === 'alias') {
        return aliasCommand(tokens);
    } else if (frontToken === 'delete') {
        return deleteCommand(tokens);
    } else if (JSON.parse(localStorage.aliases)[frontToken]) {
        return callAlias(frontToken, Array.from(tokens).join(' '));
    } else {
        return {
            message: `Rolling ${str}:`,
            rolls: [compoundRoll(str)],
        };
    }
}