class HomeController < ApplicationController
  def index
    # for tab auto-loading,
    # registered menu. :id must equal to key.
    menu = {
      "servers" => {:id=>"servers", :name=>"All Servers", :url=>"/servers"},
      "wiki" => {:id=>"wiki", :name=>"Wiki", :url=>"/wikis"},
    }
    @tab_id = menu[params[:tab]][:id]
    @tab_name = menu[params[:tab]][:name]
    @tab_url = menu[params[:tab]][:url]
  end

end

# vim:set ts=2 sw=2 expandtab:
