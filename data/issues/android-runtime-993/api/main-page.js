var createViewModel = require("./main-view-model").createViewModel;
var AlbumSelectActivity = $in.myinnos.awesomeimagepicker.activities.AlbumSelectActivity;
var ConstantsCustomGallery = $in.myinnos.awesomeimagepicker.helpers.ConstantsCustomGallery;
var utils = require("utils/utils");
var application = require("application");
function onNavigatingTo(args) {
    var page = args.object;
    page.bindingContext = createViewModel();
    var context = utils.ad.getApplicationContext();
    console.log("### TEST START ###");
    var myIntent = new android.content.Intent(context, AlbumSelectActivity.class);
    myIntent.putExtra(ConstantsCustomGallery.INTENT_EXTRA_LIMIT, 5); // set limit for image selection
    application.android.foregroundActivity.startActivityForResult(myIntent, ConstantsCustomGallery.REQUEST_CODE);
    console.log("###TEST API PASSED###");
    console.log("### TEST END ###");
}
exports.onNavigatingTo = onNavigatingTo;