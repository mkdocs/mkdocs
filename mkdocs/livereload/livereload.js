function livereload(epoch, requestId) {
    var req = new XMLHttpRequest();
    req.onloadend = function() {
        if (parseFloat(this.responseText) > epoch) {
            location.reload();
            return;
        }
        var launchNext = livereload.bind(this, epoch, requestId);
        if (this.status === 200) {
            launchNext();
        } else {
            setTimeout(launchNext, 3000);
        }
    };
    req.open("GET", "/livereload/" + epoch + "/" + requestId);
    req.send();

    console.log('Enabled live reload');
}
