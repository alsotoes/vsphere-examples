#!/usr/bin/perl -w

use strict;
use warnings;
use VMware::VIRuntime;
use VMware::VILib;
use JSON;

my ($vc_name,$vcVersion,$entity_views,$psearch);
my %opts = (
	server => {
		type => "=s",
		help => "Server IP or ServerName",
		required => 1,
	},
        psearch => {
                type => "=s",
                help => "Search param case insensitive (Linux, Windows, Other, etc)",
                required => 0,
        }
);

Opts::add_options(%opts);
Opts::parse();
Opts::validate();
Util::connect();

$vc_name = Opts::get_option('server');
$psearch = Opts::get_option('psearch') || '.';

$entity_views = Vim::find_entity_views(
	view_type => 'VirtualMachine',
	properties => [ 'name', 'config' ],
	filter => { 
		'config.template' => 'true',
		'config.guestFullName' => qr/$psearch/i,
		'runtime.powerState' => 'poweredOff'
	} 
);

my @images;
foreach my $entity_view (@$entity_views) {
	my %rec_hash = ( 
		'id' => $entity_view->config->uuid,
		'name' => $entity_view->name,
		'kind' => $entity_view->config->guestFullName,
		'tags' => $entity_view->config->annotation,
		'updated_at' => $entity_view->config->changeVersion,
		'file' => $entity_view->config->files->vmPathName
	);
	push( @images, \%rec_hash);
}
#print encode_json @images;
print JSON->new->utf8->encode( { images => \@images });

Util::disconnect();

BEGIN {
	$ENV{PERL_LWP_SSL_VERIFY_HOSTNAME} = 0;
}
