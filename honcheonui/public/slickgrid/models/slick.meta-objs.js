(function ($) {
	/***
	 * copied from slick.remotemodel.js, ajax example of slickgrid.
	 * returns {:meta => {}, :objs => {object,...}}
	 */

	function RemoteModel(url) {
		// private
		var PAGESIZE = 50;
		var data = new Array;
		var searchstr = "apple";
		var sortcol = null;
		var sortdir = 1;
		var h_request = null;
		var req = null; // ajax request

		// events
		var onDataLoading = new Slick.Event();
		var onDataLoaded = new Slick.Event();


		function init() {
		}


		function isDataLoaded(from, to) {
			for (var i = from; i <= to; i++) {
				if (data[i] == undefined || data[i] == null) {
					return false;
				}
			}
			return true;
		}


		function clear() {
			for (var key in data) {
				delete data[key];
			}
		}


		function ensureData(from, to) {
			if (req) {
				req.abort();
				for (var i = req.fromPage; i <= req.toPage; i++)
					data[i * PAGESIZE] = undefined;
			}

			if (from < 0) {
				from = 0;
			}

			var fromPage = Math.floor(from / PAGESIZE);
			var toPage = Math.floor(to / PAGESIZE);

			while (data[fromPage * PAGESIZE] !== undefined && fromPage < toPage)
				fromPage++;

			while (data[toPage * PAGESIZE] !== undefined && fromPage < toPage)
				toPage--;

			if (fromPage > toPage || ((fromPage == toPage) && data[fromPage * PAGESIZE] !== undefined)) {
				// TODO:	look-ahead
				return;
			}

			/*
			switch (sortcol) {
				case "diggs":
					url += ("&sort=" + ((sortdir > 0) ? "digg_count-asc" : "digg_count-desc"));
					break;
			}
			*/

			if (h_request != null) {
				clearTimeout(h_request);
			}

			h_request = setTimeout(function () {
				for (var i = fromPage; i <= toPage; i++)
					data[i * PAGESIZE] = null;
					// null indicates a 'requested but not available yet'

				onDataLoading.notify({from: from, to: to});

				req = $.ajax({
					url: url,
					dataType: 'json',
					success: onSuccess,
					error: function(){
						onError(fromPage, toPage)
					}
				});

				req.fromPage = fromPage;
				req.toPage = toPage;
			}, 50);
		}


		function onError(fromPage, toPage) {
			alert("error loading pages " + fromPage + " to " + toPage);
		}


		function onSuccess(resp) {
			var from = req.fromPage * PAGESIZE, to = from + resp.objs.length;

			for (var i = 0; i < resp.objs.length; i++) {
				data[from + i] = resp.objs[i];
				data[from + i].index = from + i;
			}
			req = null;
			onDataLoaded.notify({from: from, to: to});
		}


		function reloadData(from, to) {
			for (var i = from; i <= to; i++) {
				delete data[i];
			}
			ensureData(from, to);
		}


		function setSort(column, dir) {
			sortcol = column;
			sortdir = dir;
			clear();
		}

		function setSearch(str) {
			searchstr = str;
			clear();
		}



		init();

		return {
			// properties
			"data": data,

			// methods
			"clear": clear,
			"isDataLoaded": isDataLoaded,
			"ensureData": ensureData,
			"reloadData": reloadData,
			"setSort": setSort,
			"setSearch": setSearch,

			// events
			"onDataLoading": onDataLoading,
			"onDataLoaded": onDataLoaded
		};
	}

	// Slick.Data.RemoteModel
	$.extend(true, window, { Slick: { Data: { RemoteModel: RemoteModel }}});
})(jQuery);

/* vim:set ts=2 sw=2: */