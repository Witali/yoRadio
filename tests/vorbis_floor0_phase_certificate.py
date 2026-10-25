"""Exact-rational certificate for the finite-binary64 floor0 phase grid.

This proves the 2304-bit 2/pi table and a uniform nonzero phase separation;
source reduction equivalence remains a separate review/runtime check. It does
not prove libm sine accuracy or the complete floating error budget.
No SDK, compiler, decoder or external program is used.

Machin's identity follows by exact tangent addition:
tan(2*atan(1/5))=5/12, tan(4*atan(1/5))=120/119, and
tan(4*atan(1/5)-atan(1/239))=1 with the angle in (0,pi/2).
Each alternating arctangent series is bounded by adjacent partial sums.

For continued fractions we use best approximation of the second kind:
q_n<=B<q_(n+1) implies |q*pi-p| >= |q_n*pi-p_n| for 1<=q<=B.
An interval with an identical CF prefix at both endpoints certifies those
convergents; exact interval evaluation supplies a strict positive lower bound.
See https://courses.mai.liu.se/GU/TATA54/Lectures/lecture7.pdf .
"""
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import re


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def atan_interval(reciprocal, precision_bits):
    """Strict lower/upper bounds, from consecutive alternating partial sums."""
    need(reciprocal >= 2 and precision_bits >= 1, 'positive reciprocal/precision')
    epsilon = Fraction(1, 1 << (precision_bits+8))
    total, term = Fraction(0), Fraction(1, reciprocal)
    for count in range(1, precision_bits+65):
        total += term
        term *= Fraction(-(2*count-1), (2*count+1)*reciprocal*reciprocal)
        if abs(term) < epsilon:
            lower, upper = sorted((total, total+term))
            return lower, upper, count
    raise ValueError('alternating remainder precision was not reached')


def pi_interval(precision_bits=3200):
    a, b, count5 = atan_interval(5, precision_bits)
    c, d, count239 = atan_interval(239, precision_bits)
    lower, upper = 16*a-4*d, 16*b-4*c
    need(3 < lower < upper < 4 and upper-lower < Fraction(1, 1 << precision_bits),
         'strict Machin pi interval')
    return lower, upper, dict(atan5_terms=count5, atan239_terms=count239)


def fraction_record(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator))


def cf_linear_form_certificate(pi_lower, pi_upper, bound):
    """Certify a strict lower bound for every integer |q*pi-p|, 1<=q<=B."""
    need(bound >= 2 and 3 < pi_lower < pi_upper < 4, 'CF certificate inputs')
    lower, upper = pi_lower, pi_upper
    p0, p1, q0, q1 = 0, 1, 1, 0
    coefficients = []
    for _ in range(4096):
        a = lower.numerator//lower.denominator
        need(a == upper.numerator//upper.denominator, 'pi interval insufficient for an exact CF prefix')
        coefficients.append(a)
        p, q = a*p1+p0, a*q1+q0
        need(abs(p*q1-p1*q) == 1, 'consecutive convergent determinant')
        if q > bound:
            need(1 <= q1 <= bound, 'last/next convergent bracket denominator bound')
            error_lower, error_upper = q1*pi_lower-p1, q1*pi_upper-p1
            need(error_lower*error_upper > 0, 'pi interval must separate convergent error from zero')
            delta = min(abs(error_lower), abs(error_upper))
            exponent = max(0, delta.denominator.bit_length()-delta.numerator.bit_length()+1)
            while Fraction(1, 1 << exponent) >= delta:
                exponent += 1
            return dict(bound=str(bound), coefficients=coefficients,
                        last_numerator=str(p1), last_denominator=str(q1),
                        next_numerator=str(p), next_denominator=str(q),
                        strict_linear_form_lower_bound=fraction_record(delta),
                        strict_power_two_lower_bound_exponent=exponent)
        need(lower-a > 0, 'strict irrational complete-quotient interval')
        lower, upper = 1/(upper-a), 1/(lower-a)
        p0, p1, q0, q1 = p1, p, q1, q
    raise ValueError('CF denominator bound was not crossed')


def certify_source(source, precision_bits=3200):
    """Pure source-text/table certificate, never compile/import its contents."""
    lower, upper, counts = pi_interval(precision_bits)
    table_bits, phase_bits = 2304, 1152
    scale = 1 << (table_bits+1)
    table_lower = scale*upper.denominator//upper.numerator
    table_upper = scale*lower.denominator//lower.numerator
    need(table_lower == table_upper, 'strict interval uniquely determines floor((2/pi)*2^2304)')
    arrays = re.findall(r'static\s+const\s+uint32_t\s+floor0_two_over_pi\s*\[\s*PHASE_TABLE_WORDS\s*\]\s*=\s*\{(.*?)\};', source, re.S)
    need(len(arrays) == 1, 'one exact C 2/pi limb array')
    pattern = re.compile(r'UINT32_C\(\s*0x([0-9a-fA-F]{8})\s*\)')
    limbs, cursor = [], 0
    for match in pattern.finditer(arrays[0]):
        need(re.fullmatch(r'\s*' if not limbs else r'\s*,\s*', arrays[0][cursor:match.start()]), 'literal C limb separators')
        limbs.append(int(match[1], 16)); cursor = match.end()
    need(len(limbs) == 72 and re.fullmatch(r'\s*,?\s*', arrays[0][cursor:]) and
         sum(word << (32*i) for i, word in enumerate(limbs)) == table_lower, 'all72 exact little-endian limbs')
    for name, value in (('PHASE_FRACTION_WORDS', 36), ('PHASE_WORDS', 37), ('PHASE_TABLE_WORDS', 72)):
        need(re.findall(r'\b'+name+r'\s*=\s*(\d+)\b', source) == [str(value)], 'fixed C phase dimensions')
    large = cf_linear_form_certificate(lower, upper, 1 << 1042)
    small = cf_linear_form_certificate(lower, upper, 1 << 88)
    # Let epsilon=2*phi/pi +/- 2*k/L -4*n in [-2,2] after folding,
    # t=2*n*L -/+ k, phi=sign*M*2^e, 0<M<2^53, L<2^16.
    # P=sign(t)*sign*M*L*2^max(e,0) is an integer of either sign.
    # If t=0, then k=n=0: nonzero phi gives |epsilon|>2^-1075.
    # If |phi|<2^-17 and k>0, theta_min=pi/65535 separates both
    # sine arguments from a zero by more than 2^-16 phase units.
    # Otherwise e>=-69. For e>=0, Q=|t|<2^1042 and
    # |epsilon|=2/(pi*L)*|Q*pi-P| >2^-17*delta_large.
    # For e<0, Q=|t|*2^-e <= M*L/pi+2*L*2^69 <2^88,
    # and the extra factor2^e is >=2^-69. Thus the small-Q
    # bound is |epsilon|>2^-(17+69)*delta_small.
    global_gap_exponent = max(1075, 17+large['strict_power_two_lower_bound_exponent'],
                              86+small['strict_power_two_lower_bound_exponent'])
    need(global_gap_exponent <= 1100, 'global nonzero phase separation insufficient for fixed1152 grid')
    # The table truncation contributes <2^-128 FIXED units at DBL_MAX.
    # Angle and rational-bin truncations each contribute <1 unit. Folding
    # is 1-Lipschitz on the phase circle, so 3 fixed units suffice.
    rho = Fraction(3, 1 << (phase_bits-global_gap_exponent))
    # sin(pi*x/4) is positive, increasing and concave on0<x<=2, so
    # relative sine error from a phase perturbation is <=|dx|/x.
    # Each P/Q term has at most512 sine factors counting squares and
    # endpoints. Their positive sum inherits the same relative bound.
    phase_only_denominator_bound = (1+rho)**512-1
    need(phase_only_denominator_bound < Fraction(1, 10**12), 'phase-only denominator budget exceeds1e-12')
    return dict(schema='native-vorbis-floor0-phase-certificate-v1', completed=True,
                source_sha256=hashlib.sha256(source.encode('utf-8')).hexdigest(),
                pi_precision_bits=precision_bits, pi_interval_strict=True, pi_series_counts=counts,
                pi_lower=fraction_record(lower), pi_upper=fraction_record(upper),
                table_bits=table_bits, phase_fraction_bits=phase_bits,
                exact_2_over_pi_floor_hex=format(table_lower, '0576x'), little_endian_limb_count=72,
                table_truncation_max_fixed_units_less_than_power_two=-128,
                cf_large=large, cf_small=small, full_finite_binary64_nonzero_gap_exponent=global_gap_exponent,
                retained_nonzero_phase_significant_bits_at_least=phase_bits-global_gap_exponent,
                phase_relative_error_upper=dict(numerator=3, power_two_denominator=phase_bits-global_gap_exponent),
                phase_only_denominator_relative_error_less_than='1e-12',
                compiled_reduction_qualified=False, libm_or_total_floating_error_qualified=False,
                decoder_or_PCM_qualified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); need(not args.output.exists(), 'fresh certificate output')
    before = args.source.read_bytes(); result = certify_source(before.decode('utf-8'))
    need(args.source.read_bytes() == before, 'source unchanged during certificate')
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('completed', 'source_sha256',
        'full_finite_binary64_nonzero_gap_exponent', 'retained_nonzero_phase_significant_bits_at_least',
        'phase_only_denominator_relative_error_less_than')}))


if __name__ == '__main__':
    main()
