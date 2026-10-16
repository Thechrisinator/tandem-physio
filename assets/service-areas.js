const directory = document.querySelector('#suburb-directory');

if (directory) {
  const controls = directory.querySelector('[data-directory-controls]');
  const input = directory.querySelector('#suburb-search');
  const reset = directory.querySelector('[data-directory-reset]');
  const count = directory.querySelector('[data-directory-count]');
  const empty = directory.querySelector('[data-directory-empty]');
  const entries = directory.querySelectorAll('[data-suburb]');
  const normalise = (value) => value.trim().replace(/\s+/g, ' ').toLocaleLowerCase('en-AU');

  const filter = () => {
    const query = normalise(input.value);
    let matches = 0;
    entries.forEach((entry) => {
      entry.hidden = !normalise(entry.querySelector('.suburb-name').textContent).includes(query);
      if (!entry.hidden) matches += 1;
    });
    count.textContent = `${matches} of ${entries.length} suburbs shown`;
    empty.hidden = matches !== 0;
  };

  input.addEventListener('input', filter);
  reset.addEventListener('click', () => {
    input.value = '';
    filter();
    input.focus();
  });
  filter();
  controls.hidden = false;
}
