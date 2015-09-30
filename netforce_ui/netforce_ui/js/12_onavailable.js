/*jshint browser: true, jquery: true, indent: 2, white: true, curly: true, forin: true, noarg: true, immed: true, newcap: true, noempty: true, nomen: true*/

(function ($)
{
  var watchedSelectors = [],
      watcher,
      watcherInterval,
      domEventHandler,
      domEventString = 'DOMNodeInserted DOMSubtreeModified';

  $.fn.onavailable = function (callback)
  {
    if (this.length)
    {
      callback.call(this[0]);
    }
    else
    {
      watchedSelectors.push([this.selector, callback]);
      
      if ($.browser.webkit || $.browser.mozilla)
      {
        if (watchedSelectors.length === 1)
        {
          $(document).bind(domEventString, domEventHandler);
        }
      }
      else
      {
        if (!watcherInterval)
        {
          watcherInterval = setInterval(watcher, $.browser.msie ? 250 : 75);
        }
      }
    }
  };
  
  domEventHandler = function ()
  {
    $(watchedSelectors).each(function (i, items) {
      var target = event.target;
      if ($(target).is(items[0]))
      {
        items[1].call(target);
        watchedSelectors.splice(i, 1);
      }
    });
    
    if (!watchedSelectors.length)
    {
      $(document).unbind(domEventString, domEventHandler);
    }
  };
  
  watcher = function ()
  {
    $(watchedSelectors).each(function (i, items) {
      var results = $(items[0]);
      if (results[0])
      {
        items[1].call(results[0]);
        watchedSelectors.splice(i, 1);
      }
    });
    
    if (!watchedSelectors.length)
    {
      clearInterval(watcherInterval);
      watcherInterval = null;
    }
  };
}(jQuery));
