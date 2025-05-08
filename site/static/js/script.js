document.getElementById('download_btn').onclick = download_track;

function download_track() {
    const title = document.getElementById('title').value;
    fetch(`/download_track_api/${encodeURIComponent(title)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(() => {
        alert("Скачано");
    })
    .catch(err => console.error(err));
}