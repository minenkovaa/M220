async function showWorksheet() {
const num = prompt("Enter your number:");
const xml =
await fetch("problems.xml")
.then(r => r.text());
const parser = new DOMParser();
const doc =
parser.parseFromString(xml,"text/xml");
const problem =
doc.querySelector(
`problem[number="${num}"]`
);
document.getElementById(
"worksheet-app"
).innerHTML =
problem.querySelector("A").textContent;
}