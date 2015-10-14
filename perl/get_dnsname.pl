#!/usr/bin/perl -w

use strict;
use warnings;
use VMware::VIRuntime;
use VMware::VILib;
use MIME::Base64;

my ($vc_name,$vcVersion,$entity_views);

my %opts = (
        server => {
                type => "=s",
                help => "Server IP or ServerName",
                required => 1,
        },
);

Opts::add_options(%opts);
Opts::parse();
Opts::validate();
Util::connect();

$entity_views = Vim::find_entity_views(
	view_type => 'VirtualMachine',
	properties => ['name', 'guest','config'],
	filter => {
		'config.template' => 'false',
		'runtime.powerState' => 'poweredOn'
	}
	#filter => {"name" => qr/^$vmName/i}
);

foreach my $vm (@$entity_views) {
	my $vmName = $vm->{'name'} || "No VMName";
	my $DNSname = $vm->guest->hostName || "No DNS Name";
	print "Name 	: $vmName "."(".$vm->config->uuid.")\n";
	print "DNS Name : $DNSname\n\n";
}

Util::disconnect();

BEGIN {
        $ENV{PERL_LWP_SSL_VERIFY_HOSTNAME} = 0;
}
