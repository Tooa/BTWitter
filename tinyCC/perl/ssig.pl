#!/usr/bin/perl -w
use Math::Trig;
# ssig tahes .sfreq and .count and computes ll scores
# parameters:
#  - word list unique: w_nr, u-freq
#  - sfreq: w_nr1, w_nr2, count
# by Chris Biemann, SEP 2006
#
#
#
# usage

sub log2 {
	my $n = shift;
    return log($n)/log(2);
}

if (@ARGV ne 6) {die "Parameters (6): freq-wordlist index sfreq MINSIG PREC outname";}


$MINSIG=$ARGV[3];
$PREC=10**$ARGV[4];
$OUTFILE=$ARGV[5];



# read in frequencies
open(WL,"<$ARGV[0].unique");

$maxnr=0;

%nrToFreq=();
while($in=<WL>) {
  chomp($in);
  @a=split(/\t/,$in);
  $nrToFreq{$a[0]}=$a[1];            # unique counts for sentences
  if ($a[0]>$maxnr) {$maxnr=$a[0];}
} # elihw


# read number of experiments from .count file
open(COUNT,"<$ARGV[1].scount"); 
$n=<COUNT>;
chomp($n);


# scan OUTFREQ and add sig_val

open(SCOOC,">$OUTFILE");
open(OUTFREQ,"<$ARGV[2]");

# formula: log-likelihood: 
# ll= -2 log lambda = 2 * [ n log n - nA log nA - nB log nB + nAB log nAB
#		      +(n - nA - nB + nAB) log (n - nA - nB + nAB)
#		      +(nA - nAB) log (nA - nAB) + (nB - nAB) log (nB - nAB)
#		      -(n - nA) log (n - nA) - (n - nB) log (n - nB) ]
#
#  n : count of possible pairs
#  nA: count of A
#  nB count of B
#  nAB: count of joint occurrence A and B



$nonzero=0.0000000000001;
while($in=<OUTFREQ>) {
   chomp($in);
   @a=split(/\t/,$in);   
   $nA=$nrToFreq{$a[0]};
   $nB=$nrToFreq{$a[1]};
   $nAB=$a[2];
   

#   print SCOOC "n=$n nA=$nA nB=$nB nAB=$nAB at $in\n";

   $surprise= 2*($n*log($n)-$nA*log($nA)-$nB*log($nB)+$nAB*log($nAB)
        +($n-$nA-$nB+$nAB)*log($n-$nA-$nB+$nAB+$nonzero)
        +($nA-$nAB)*log($nA-$nAB+$nonzero)+($nB-$nAB)*log($nB-$nAB+$nonzero)
        -($n-$nA)*log($n-$nA+$nonzero)-($n-$nB)*log($n-$nB+$nonzero) );

   # negative or positive correlation
   if (($n * $nAB) < ($nA * $nB)) 
      { $ll=$surprise*(-1); }
   else {$ll=$surprise;}   

   # round
   $ll=int($ll*$PREC+0.5)/$PREC;

   #SigLL / nAB
   $sig1 = ($ll / $nAB);
   $sig1 = int($sig1*$PREC+0.5)/$PREC;
   #sigLL / log(nAB)
   $sig2 = ($ll / log($nAB));
   $sig2 = int($sig2*$PREC+0.5)/$PREC;
   #pmi
   $pmi = log2(($n*$nAB) / ($nA * $nB)); 
   $pmi = int($pmi*$PREC+0.5)/$PREC;
   #lmi
   $lmi = $nAB * $pmi;
   $lmi = int($lmi*$PREC+0.5)/$PREC;

   if ($sig2>=$MINSIG) {
     print SCOOC "$in\t$ll\t$sig1\t$sig2\t$pmi\t$lmi\n";
   }  
}


exit;

