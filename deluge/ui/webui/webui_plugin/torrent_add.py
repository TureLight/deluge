#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Martijn Voncken 2008 <mvoncken@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, write to:
#     The Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor
#     Boston, MA  02110-1301, USA.
#
#  In addition, as a special exception, the copyright holders give
#  permission to link the code of portions of this program with the OpenSSL
#  library.
#  You must obey the GNU General Public License in all respects for all of
#  the code used other than OpenSSL. If you modify file(s) with this
#  exception, you may extend this exception to your version of the file(s),
#  but you are not obligated to do so. If you do not wish to do so, delete
#  this exception statement from your version. If you delete this exception
#  statement from all source files in the program, then also delete it here.
#
from webserver_common import ws
import utils
from render import render, error_page
import page_decorators as deco
import lib.newforms_plus as forms
import lib.webpy022 as web
import base64

class OptionsForm(forms.Form):
    download_location =  forms.ServerFolder(_("Download Location"))
    compact_allocation = forms.CheckBox(_("Compact Allocation"))

    #download
    max_download_speed_per_torrent = forms.DelugeFloat(
        _("Maximum Down Speed"))
    max_upload_speed_per_torrent = forms.DelugeFloat(
        _("Maximum Up Speed"))
    max_connections_per_torrent = forms.DelugeInt(_("Maximum Connections"))
    max_upload_slots_per_torrent = forms.DelugeInt(_("Maximum Upload Slots"))
    #general
    prioritize_first_last_pieces = forms.CheckBox(
        _('Prioritize first and last pieces'))
    add_paused = forms.CheckBox(_('Add In Paused State'))
    default_private = forms.CheckBox(_('Set Private Flag'))

    def initial_data(self):
        return ws.proxy.get_config()

class AddForm(forms.Form):
    url = forms.CharField(label=_("Url"), required=False,
        widget=forms.TextInput(attrs={'size':60}))
    torrent = forms.CharField(label=_("Upload torrent"), required=False,
        widget=forms.FileInput(attrs={'size':60}))
    hash = forms.CharField(label=_("Hash"), required=False,
        widget=forms.TextInput(attrs={'size':60}))
    ret = forms.CheckBox(_('Add more'))

class torrent_add:

    def add_page(self,error = None):
        form_data = utils.get_newforms_data(AddForm)
        options_data = None
        if error:
            options_data = utils.get_newforms_data(OptionsForm)
        return render.torrent_add(AddForm(form_data),OptionsForm(options_data), error)

    @deco.deluge_page
    def GET(self, name):
        return self.add_page()


    @deco.check_session
    def POST(self, name):
        """
        allows:
        *posting of url
        *posting file-upload
        *posting of data as string(for greasemonkey-private)
        """

        options = dict(utils.get_newforms_data(OptionsForm))
        options_form = OptionsForm(options)
        if not options_form.is_valid():
            print self.add_page(error = _("Error in torrent options."))
            return


        vars = web.input(url = None, torrent = {})
        torrent_name = None
        torrent_data  = None
        if vars.torrent.filename:
            torrent_name = vars.torrent.filename
            torrent_data  = vars.torrent.file.read()

        if vars.url and torrent_name:
            #error_page(_("Choose an url or a torrent, not both."))
            print self.add_page(error = _("Choose an url or a torrent, not both."))
            return
        if vars.url:
            ws.proxy.add_torrent_url(vars.url, options)
            utils.do_redirect()
        elif torrent_name:
            data_b64 = base64.b64encode(torrent_data)
            #b64 because of strange bug-reports related to binary data
            ws.proxy.add_torrent_filecontent(vars.torrent.filename, data_b64, options)
            utils.do_redirect()
        else:
            print self.add_page(error = _("No data"))
            return
