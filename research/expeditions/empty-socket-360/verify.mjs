import {verify, vacancyRoute, evenRoute, directFloor, matrix} from './routing.mjs';
import assert from 'node:assert/strict';
assert.throws(()=>vacancyRoute([0,0]));
assert.throws(()=>evenRoute([1,0]));
assert.throws(()=>matrix([0],[0],-1));
assert.equal(directFloor([1,0]),0);
assert.equal(vacancyRoute([1,0]).length,4);
console.log(JSON.stringify(verify(),null,2));
