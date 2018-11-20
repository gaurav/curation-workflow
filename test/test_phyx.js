/*
 * test_phyx.js: Test all PHYX files in this repository.
 */

const BASE_DIR = 'phyx/';

// Our libraries.
const phyx2jsonld = require('../curation-tool/js/phyx2jsonld.js');

// Javascript libraries.
const child_process = require('child_process');
const fs = require('fs');
const path = require('path');
const chai = require('chai');
const assert = chai.assert;

/*
 * Returns a list of PHYX files that we can test in the provided directory.
 *
 * We use a simple flatMap to search for these files. Since flatMap isn't in
 * Node.js yet, I use a map to recursively find the files and then flatten it
 * using reduce() and concat().
 *
 * This could be implemented asynchronously, but we need a list of files to
 * test each one individually in Mocha, so we need a synchronous implementation
 * to get that list before we start testing.
 */
function findPHYXFiles(dirPath) {
    return fs.readdirSync(dirPath).map(function(filename) {
        const filePath = path.join(dirPath, filename);

        if(fs.lstatSync(filePath).isDirectory()) {
            // Recurse into this directory.
            return findPHYXFiles(filePath);
        } else {
            // Look for .json files (but not for '_as_owl.json' files, for historical reasons).
            if(filePath.endsWith('.json') && !filePath.endsWith('_as_owl.json')) {
                return [filePath];
            } else {
                return [];
            }
        }
   }).reduce((x, y) => x.concat(y), []); // This flattens the list of results.
}

// Test each input file.
describe('Test PHYX files in repository', function() {
    findPHYXFiles(BASE_DIR).forEach(function(filename) {
        describe('PHYX file: ' + filename, function() {
            it('is not empty', function() {
              const stats = fs.lstatSync(filename);
              assert.notEqual(stats["size"], 0);
            });

            // Load the PHYX data. Check to see if it is git-crypt encrypted.
            const data = fs.readFileSync(filename);
            const gitcrypt = data.slice(0, 9);
            if(gitcrypt.equals(Buffer.from("\x00GITCRYPT"))) {
                it.skip('cannot test git-encrypted file');
                return;
            }

            // Read the PHYX data as 'UTF-8' and convert it into JSON-LD.
            const phyx = data.toString('utf-8');
            var jsonld;
            try {
              jsonld = phyx2jsonld.convertPHYXToJSONLD(phyx);
            } catch(ex) {
              it('convertPHYXToJSONLD threw an exception', function() {
                throw ex;
              });
              return;
            }

            it('produced JSON-LD is not empty', function() {
              assert.isNotEmpty(jsonld);
            });

            // Test using JPhyloRef.
            var args = [
              '-jar', 'jphyloref/jphyloref.jar',
              'test', '-', '--jsonld'
            ];
            if('JVM_ARGS' in process.env) {
              args = process.env.JVM_ARGS.split(/\s+/).concat(args);
            }
            if('JPHYLOREF_ARGS' in process.env) {
              args = args.concat(process.env.JPHYLOREF_ARGS.split(/\s+/));
            }
            // console.log("args: " + args);
            const child = child_process.spawnSync('java', args, { input: jsonld });
            const matches = /Testing complete:(\d+) successes, (\d+) failures, (\d+) failures marked TODO, (\d+) skipped./.exec(child.stderr);

            it('Testing test result line from JPhyloRef', function() {
              assert.isNotNull(matches, 'Testing complete line not found in STDOUT');

              const failures = matches[2];
              assert.equal(failures, 0, failures + ' failures occurred during testing');
            });

            const successes = matches[1];
            const todos = matches[3];
            const skipped = matches[4];

            if(todos > 0) {
              it.skip(todos + ' phyloreferences were marked as TODO during testing.');
              return;
            }

            if(skipped > 0) {
              it.skip(skipped + ' phyloreferences were skipped during testing.');
              return;
            }

            // On the off chance that all of the above made sense but the exit code didn't,
            // we'll check that here.
            it('passed testing in JPhyloRef', function() {
              assert.equal(child.status, 0, 'Exit code from JPhyloRef was not zero');
              assert.isAbove(successes, 0, 'No successes occurred during testing');
            });
        });
    });
});
